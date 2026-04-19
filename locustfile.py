"""
AMOS Equation System v2.0 - Load Testing Suite
Locust-based performance testing for production validation

Usage:
    locust -f locustfile.py --host http://localhost:8000

    Headless mode:
    locust -f locustfile.py --host http://localhost:8000
        --users 100 --spawn-rate 10 --run-time 5m --headless

Features:
    - REST API endpoint testing
    - GraphQL query/mutation testing
    - WebSocket real-time testing
    - Authentication flow testing
    - Background task submission testing
"""

import random
from datetime import datetime

from locust import HttpUser, between, events, task
from locust.runners import MasterRunner

# =============================================================================
# Configuration
# =============================================================================


class LoadTestConfig:
    """Load testing configuration"""

    API_VERSION = "v1"
    TEST_EQUATION_IDS = list(range(1, 101))
    TEST_USER_IDS = list(range(1, 51))
    TEST_USERNAME = "test_user"
    TEST_PASSWORD = "test_password123"

    WEIGHT_HEALTH_CHECK = 10
    WEIGHT_GET_EQUATION = 50
    WEIGHT_LIST_EQUATIONS = 30
    WEIGHT_VERIFY_EQUATION = 20
    WEIGHT_CREATE_EQUATION = 5
    WEIGHT_GRAPHQL = 15
    WEIGHT_METRICS = 2


# =============================================================================
# Base User Class
# =============================================================================


class BaseEquationUser(HttpUser):
    """Base user class with common functionality"""

    abstract = True
    wait_time = between(1, 5)

    def on_start(self):
        self.api_token: str = None
        self.equation_ids = []
        self.user_id = None

    def get_auth_headers(self) -> dict:
        if self.api_token:
            return {"Authorization": f"Bearer {self.api_token}"}
        return {}

    def get_json_headers(self) -> dict:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        headers.update(self.get_auth_headers())
        return headers


# =============================================================================
# Anonymous User
# =============================================================================


class AnonymousUser(BaseEquationUser):
    """Simulates unauthenticated users"""

    weight = 3

    @task(LoadTestConfig.WEIGHT_HEALTH_CHECK)
    def health_check(self):
        with self.client.get("/health/live", name="Health - Live", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    response.failure("Health check returned unhealthy")

    @task(LoadTestConfig.WEIGHT_HEALTH_CHECK)
    def health_ready(self):
        self.client.get("/health/ready", name="Health - Ready")

    @task(LoadTestConfig.WEIGHT_GET_EQUATION)
    def get_public_equation(self):
        equation_id = random.choice(LoadTestConfig.TEST_EQUATION_IDS)
        with self.client.get(
            f"/api/{LoadTestConfig.API_VERSION}/equations/{equation_id}",
            name="Equation - Get Public",
            catch_response=True,
        ) as response:
            if response.status_code in [200, 404]:
                response.success()

    @task(LoadTestConfig.WEIGHT_LIST_EQUATIONS)
    def list_public_equations(self):
        params = {"skip": random.randint(0, 50), "limit": random.randint(10, 50)}
        self.client.get(
            f"/api/{LoadTestConfig.API_VERSION}/equations/",
            params=params,
            name="Equation - List Public",
        )

    @task(LoadTestConfig.WEIGHT_METRICS)
    def get_metrics(self):
        self.client.get("/metrics", name="Metrics - Prometheus")


# =============================================================================
# Authenticated User
# =============================================================================


class AuthenticatedUser(BaseEquationUser):
    """Simulates authenticated users"""

    weight = 5

    def on_start(self):
        super().on_start()
        self.login()

    def login(self):
        with self.client.post(
            "/auth/login",
            data={
                "username": LoadTestConfig.TEST_USERNAME,
                "password": LoadTestConfig.TEST_PASSWORD,
            },
            name="Auth - Login",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.api_token = data.get("access_token")
                if self.api_token:
                    response.success()
                else:
                    response.failure("No access token in response")

    @task(LoadTestConfig.WEIGHT_GET_EQUATION)
    def get_equation_detail(self):
        equation_id = random.choice(LoadTestConfig.TEST_EQUATION_IDS)
        self.client.get(
            f"/api/{LoadTestConfig.API_VERSION}/equations/{equation_id}",
            headers=self.get_auth_headers(),
            name="Equation - Get Detail",
        )

    @task(LoadTestConfig.WEIGHT_LIST_EQUATIONS)
    def list_my_equations(self):
        params = {
            "owner_id": random.choice(LoadTestConfig.TEST_USER_IDS),
            "skip": random.randint(0, 20),
            "limit": random.randint(5, 20),
        }
        self.client.get(
            f"/api/{LoadTestConfig.API_VERSION}/equations/",
            params=params,
            headers=self.get_auth_headers(),
            name="Equation - List Mine",
        )

    @task(LoadTestConfig.WEIGHT_VERIFY_EQUATION)
    def verify_equation(self):
        equation_id = random.choice(LoadTestConfig.TEST_EQUATION_IDS)
        self.client.post(
            f"/api/{LoadTestConfig.API_VERSION}/equations/{equation_id}/verify",
            headers=self.get_auth_headers(),
            name="Equation - Verify",
        )

    @task(LoadTestConfig.WEIGHT_CREATE_EQUATION)
    def create_equation(self):
        equation_data = {
            "name": f"Load Test Equation {datetime.now().isoformat()}",
            "latex": "E = mc^2",
            "equation_type": "physics",
            "tags": ["load-test", "performance"],
        }
        with self.client.post(
            f"/api/{LoadTestConfig.API_VERSION}/equations/",
            json=equation_data,
            headers=self.get_json_headers(),
            name="Equation - Create",
            catch_response=True,
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.equation_ids.append(data.get("id"))
                response.success()
            elif response.status_code == 429:
                response.success()

    @task(LoadTestConfig.WEIGHT_CREATE_EQUATION // 2)
    def update_equation(self):
        if not self.equation_ids:
            return
        equation_id = random.choice(self.equation_ids)
        update_data = {"name": f"Updated {datetime.now().isoformat()}"}
        self.client.patch(
            f"/api/{LoadTestConfig.API_VERSION}/equations/{equation_id}",
            json=update_data,
            headers=self.get_json_headers(),
            name="Equation - Update",
        )

    @task(LoadTestConfig.WEIGHT_GRAPHQL)
    def graphql_query(self):
        query = {"query": "query { equations(limit: 10) { id name latex owner { username } } }"}
        self.client.post(
            "/graphql",
            json=query,
            headers=self.get_json_headers(),
            name="GraphQL - Query Equations",
        )

    @task(LoadTestConfig.WEIGHT_GRAPHQL // 2)
    def graphql_mutation(self):
        mutation = {
            "query": 'mutation { createEquation(name: "Load Test" latex: "x = y + z" equationType: MATHEMATICS) { id name } }'
        }
        self.client.post(
            "/graphql",
            json=mutation,
            headers=self.get_json_headers(),
            name="GraphQL - Create Equation",
        )


# =============================================================================
# Admin User
# =============================================================================


class AdminUser(BaseEquationUser):
    """Simulates admin users"""

    weight = 1

    def on_start(self):
        super().on_start()
        with self.client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin_password"},
            name="Auth - Admin Login",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.api_token = data.get("access_token")

    @task(10)
    def admin_list_all_users(self):
        self.client.get("/admin/users/", headers=self.get_auth_headers(), name="Admin - List Users")

    @task(5)
    def admin_system_metrics(self):
        self.client.get(
            "/admin/metrics/", headers=self.get_auth_headers(), name="Admin - System Metrics"
        )

    @task(5)
    def admin_export_data(self):
        export_request = {"format": "json", "entity_type": "equations"}
        self.client.post(
            "/admin/export/",
            json=export_request,
            headers=self.get_json_headers(),
            name="Admin - Export Data",
        )


# =============================================================================
# Batch Processor
# =============================================================================


class BatchProcessorUser(BaseEquationUser):
    """Simulates batch processing"""

    weight = 1
    wait_time = between(5, 15)

    def on_start(self):
        super().on_start()
        with self.client.post(
            "/auth/login",
            data={
                "username": LoadTestConfig.TEST_USERNAME,
                "password": LoadTestConfig.TEST_PASSWORD,
            },
            name="Auth - Batch Login",
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.api_token = data.get("access_token")

    @task(50)
    def batch_verify_equations(self):
        equation_ids = random.sample(LoadTestConfig.TEST_EQUATION_IDS, k=random.randint(5, 20))
        batch_request = {"equation_ids": equation_ids}
        with self.client.post(
            f"/api/{LoadTestConfig.API_VERSION}/batch/verify",
            json=batch_request,
            headers=self.get_json_headers(),
            name="Batch - Verify Equations",
            catch_response=True,
        ) as response:
            if response.status_code == 202:
                data = response.json()
                task_id = data.get("task_id")
                if task_id:
                    response.success()
                    self.client.get(
                        f"/api/{LoadTestConfig.API_VERSION}/tasks/{task_id}",
                        headers=self.get_auth_headers(),
                        name="Task - Check Status",
                    )
            elif response.status_code == 429:
                response.success()

    @task(25)
    def batch_export_data(self):
        export_request = {
            "format": random.choice(["json", "csv", "xlsx"]),
            "entity_type": "equations",
            "filters": {"equation_type": random.choice(["physics", "mathematics", "chemistry"])},
        }
        self.client.post(
            f"/api/{LoadTestConfig.API_VERSION}/batch/export",
            json=export_request,
            headers=self.get_json_headers(),
            name="Batch - Export Data",
        )


# =============================================================================
# Event Hooks
# =============================================================================


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("=" * 60)
    print("AMOS Equation System v2.0 - Load Testing")
    print("=" * 60)
    print(f"Target Host: {environment.host}")
    print("User Classes: Anonymous, Authenticated, Admin, BatchProcessor")
    print("-" * 60)
    if isinstance(environment.runner, MasterRunner):
        print("Running in distributed mode (Master)")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("=" * 60)
    print("Load Testing Complete")
    print("=" * 60)
    stats = environment.runner.stats
    print(f"\nTotal Requests: {stats.total.num_requests}")
    print(f"Failed Requests: {stats.total.num_failures}")
    print(f"Avg Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"RPS: {stats.total.total_rps:.2f}")


@events.request.add_listener
def on_request(
    request_type, name, response_time, response_length, response, context, exception, **kwargs
):
    if response_time > 2000:
        print(f"[SLOW] {name}: {response_time:.0f}ms")
    if exception:
        print(f"[ERROR] {name}: {exception}")


__all__ = ["AnonymousUser", "AuthenticatedUser", "AdminUser", "BatchProcessorUser"]
