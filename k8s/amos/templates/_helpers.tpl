{{/*
AMOS Helm Chart Helpers
*/}}

{{/* Expand the name of the chart */}}
{{- define "amos.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/* Create a default fully qualified app name */}}
{{- define "amos.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/* Create chart name and version */}}
{{- define "amos.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/* Common labels */}}
{{- define "amos.labels" -}}
helm.sh/chart: {{ include "amos.chart" . }}
{{ include "amos.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/* Selector labels */}}
{{- define "amos.selectorLabels" -}}
app.kubernetes.io/name: {{ include "amos.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/* Create the name of the service account */}}
{{- define "amos.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "amos.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- default "default" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}

{{/* Database connection string */}}
{{- define "amos.database.url" -}}
{{- printf "postgresql+asyncpg://%s:%s@%s-postgresql:5432/%s"
    .Values.postgresql.auth.username
    .Values.postgresql.auth.password
    (include "amos.fullname" .)
    .Values.postgresql.auth.database -}}
{{- end -}}

{{/* Redis connection string */}}
{{- define "amos.redis.url" -}}
{{- printf "redis://:%s@%s-redis-master:6379/0"
    .Values.redis.auth.password
    (include "amos.fullname" .) -}}
{{- end -}}

{{/* Kafka bootstrap servers */}}
{{- define "amos.kafka.bootstrap" -}}
{{- printf "%s-kafka:9092" (include "amos.fullname" .) -}}
{{- end -}}

{{/* API hostname */}}
{{- define "amos.api.host" -}}
{{- if .Values.ingress.enabled -}}
{{- (index .Values.ingress.hosts 0).host -}}
{{- else -}}
{{- printf "%s-api" (include "amos.fullname" .) -}}
{{- end -}}
{{- end -}}

{{/* Check if monitoring is enabled */}}
{{- define "amos.monitoring.enabled" -}}
{{- if and .Values.monitoring.enabled .Values.monitoring.prometheus.enabled -}}
true
{{- else -}}
false
{{- end -}}
{{- end -}}
