{\rtf1\ansi\ansicpg1252\cocoartf2867
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # AMOS_CHATGPT_BOOTSTRAP.md  \
## Official Bootstrap for All ChatGPT Conversations  \
**Owner: Trang**  \
**System: AMOS \'97 Autonomous Multi-Operator System**\
\
This file must be followed by ChatGPT in every conversation that references AMOS.  \
It ensures deterministic behaviour, correct naming, correct Python version, correct repo, and consistent system expansion.\
\
---\
\
# 1. ROOT SYSTEM RULES\
\
ChatGPT must automatically apply these rules:\
\
- Python version must always be:  \
  `/usr/bin/python3`  \
- AMOS root path must always be:  \
  `/Users/trangphan/Documents/GitHub/AMOS-PUBLIC`\
- Never generate code requiring external packages unless explicitly allowed.\
- Never overwrite existing canon JSON or Python modules unless instructed.\
- Always preserve deterministic naming:\
  - `<SYSTEM>.json`\
  - `<KernelName>_Kernel.json`\
  - `<EngineName>_Engine.json`\
  - `<AgentName>_Agent.json`\
- Always update the registry when new components are created.\
- When the user asks for a **terminal script**, return **pure commands only**, no comments.\
\
When user says \'93max power\'94 \uc0\u8594   \
ChatGPT must generate the most exhaustive, scalable, deterministic, fully governed version.\
\
---\
\
# 2. ABSOLUTE SYSTEM PATHS (ALWAYS USE THESE)\
\
```\
AMOS_ROOT=/Users/trangphan/Documents/GitHub/AMOS-PUBLIC\
PYTHON=/usr/bin/python3\
```\
\
---\
\
# 3. ONE-CLICK FULL SYSTEM BUILD\
\
The official AMOS full rebuild command:\
\
```\
cd /Users/trangphan/Documents/GitHub/AMOS-PUBLIC\
/usr/bin/python3 AMOS_BUILD_EVERYTHING.py\
/usr/bin/python3 AMOS_ONECLICK_ORCHESTRATOR.py\
git add .\
git commit -m "AMOS full build + orchestration run"\
git push\
```\
\
This pipeline performs:\
\
1. Canon generation  \
2. Kernel/Engine/Agent creation  \
3. Layout builder  \
4. Wiring pass  \
5. Speed optimisation  \
6. Full benchmark  \
7. Registry rebuild  \
8. Git sync\
\
---\
\
# 4. OFFICIAL CANON RULES\
\
AMOS must always maintain this deterministic tree:\
\
```\
AMOS_CANON/\
    SYSTEMS/\
    KERNELS/<SYSTEM>/\
    ENGINES/<SYSTEM>/\
    AGENTS/<SYSTEM>/\
    registry.json\
```\
\
Each component obeys:\
\
```\
<SYSTEM>.json\
<KernelName>_Kernel.json\
<EngineName>_Engine.json\
<AgentName>_Agent.json\
```\
\
Python modules must be placed beside JSON if required.\
\
---\
\
# 5. MASTER GENERATION SCRIPTS (MANDATORY)\
\
AMOS_BUILD_EVERYTHING.py  \
AMOS_BUILD_ALL_AGENTS.py  \
AMOS_BUILD_ALL_ENGINES.py  \
AMOS_BUILD_ALL_KERNELS.py  \
\
These scripts:\
\
- read the official system definition  \
- create all JSON files  \
- create all Python agent stubs  \
- never overwrite existing files  \
- regenerate registry  \
- ensure full structural integrity  \
\
---\
\
# 6. CHATGPT BEHAVIOUR RULES\
\
ChatGPT must automatically:\
\
- Reload this bootstrap whenever the user referencing AMOS enters a conversation.\
- Always infer the current state of AMOS from GitHub repo `trangyp/AMOS-PUBLIC`.\
- Use only deterministic naming.\
- Respect Trang\'92s authority over system rules (\'93governed by Trang\'94).\
- Generate scalable, exhaustive system components when requested.\
- Produce 100% Python-3.9-compatible code.\
\
When user asks:\
\
### \'93next\'94, \'93continue\'94, \'93max power\'94, \'93expand\'94, \'93upgrade\'94\
ChatGPT must:\
- choose the highest-power deterministic expansion  \
- identify missing components  \
- generate full scripts  \
- update all canon folders  \
- provide next steps  \
\
---\
\
# 7. TERMINAL SCRIPT MODE\
\
When user requests:  \
**\'93terminal only\'94, \'93just commands\'94, \'93no comments\'94**\
\
ChatGPT MUST output:\
\
- NO text outside the command block  \
- NO comments inside commands  \
- NO explanation  \
\
Example:\
\
```\
cd /Users/trangphan/Documents/GitHub/AMOS-PUBLIC\
/usr/bin/python3 AMOS_BUILD_EVERYTHING.py\
git add .\
git commit -m "update"\
git push\
```\
\
---\
\
# 8. GITHUB / CODEX INTEGRATION\
\
ChatGPT must assume:\
\
- Repo `trangyp/AMOS-PUBLIC` is always readable.\
- Codex tools may be used when the user is in coding mode.\
- ChatGPT must load canonical structure from GitHub automatically whenever asked to "inspect", "analyse", or "fix".\
\
---\
\
# 9. FINAL RULE\
\
Everything produced by ChatGPT for AMOS must support:\
\
- full automation  \
- maximum scalability  \
- deterministic structure  \
- zero intellectual property leakage  \
- zero hallucination  \
- strict alignment to Trang\'92s governance  \
- strict Python 3.9 compatibility  \
\
This file is the **single source of truth**.\
\
All ChatGPT sessions must adhere to it.}