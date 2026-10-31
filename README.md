# Hello Customer — from Windows laptop to OpenShift to customer

A tiny Flask web page for learning the *complete* deployment path:

`Windows/VS Code → Git → GitHub → OpenShift S2I build → container/pod → service → HTTPS route → customer browser`

The app greets people by name. `/health` returns `{"status":"ok"}`. It has no database and stores no customer information. A GitHub Actions workflow automatically runs four tests on pushes.

## Prerequisites

- Personal GitHub account: https://github.com/
- Git for Windows: https://git-scm.com/downloads/win
- Python 3.12 on Windows: https://www.python.org/downloads/
- VS Code, optional: https://code.visualstudio.com/
- Free 30-day Red Hat OpenShift Developer Sandbox: https://developers.redhat.com/developer-sandbox
- OpenShift CLI (`oc`), downloadable from the OpenShift web console under **? → Command Line Tools**. You do *not* need to run an OpenShift cluster on your laptop.

**Security:** For this practice exercise, use a personal *public* GitHub repository with *only this demo code*. Do not upload employer code, tokens, keys, passwords, or customer data.

## Step 1 — Run the app locally (Windows PowerShell)

Extract this ZIP and open PowerShell in the `hello-customer-project` folder.

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python wsgi.py
```

Open http://127.0.0.1:5000 and try `http://127.0.0.1:5000/?name=Alex`. Open http://127.0.0.1:5000/health. Stop with Ctrl+C.

If activation is blocked by PowerShell execution policy, skip activation and use `\.venv\Scripts\python.exe -m pip install -r requirements.txt`, `\.venv\Scripts\python.exe -m unittest discover -s tests -v`, and `\.venv\Scripts\python.exe wsgi.py` instead.

## Step 2 — Save the software in Git and GitHub

On GitHub, create a new **public** repository named `hello-customer`, with no initial README, .gitignore, or license (these files are already in this project). Then, from the folder:

```powershell
git init -b main
git add .
git commit -m "Create initial customer web app"
git remote add origin https://github.com/YOUR_USERNAME/hello-customer.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username. Complete the normal GitHub sign-in when requested. Check that `wsgi.py`, `requirements.txt`, and `.github/workflows/ci.yml` appear on GitHub. Click **Actions** to see the test run. Only publish the included source files, never `.venv`.

## Step 3 — Create an OpenShift application from GitHub

1. Sign in to https://developers.redhat.com/developer-sandbox and open the OpenShift web console.
2. Install `oc` from **? → Command Line Tools** if not already installed. Close/reopen PowerShell if necessary. Check `oc version --client`.
3. Use the console's **Copy login command** (usually under the user menu or Command Line Tools) and paste the generated `oc login ...` line into PowerShell. Treat that token as a password. **Do not put it in GitHub**.
4. Select your Sandbox project. The Sandbox often supplies a project automatically. Run `oc projects`, then `oc project YOUR_SANDBOX_PROJECT`. If your cluster permits creating projects, alternatively use `oc new-project hello-customer-demo`.
5. Create the app:

```powershell
oc new-app https://github.com/YOUR_USERNAME/hello-customer.git --name=hello-customer
```

The `requirements.txt` file lets OpenShift detect Python and attempt a Source-to-Image (S2I) build. The Python S2I image detects `wsgi.py`; with `gunicorn` installed, it serves the `app` callable. No Dockerfile or local Docker installation is needed.

If OpenShift cannot find a Python builder image or guesses incorrectly, choose the cluster's Python builder from its catalog. One possible explicit source-build form is:

```powershell
oc new-app quay.io/sclorg/python-312-c9s~https://github.com/YOUR_USERNAME/hello-customer.git --name=hello-customer
```

Use this alternate command only if the first command failed without creating the app. The referenced public builder image must be reachable and allowed by your OpenShift cluster.

Check build and deployment:

```powershell
oc get builds
oc get pods
oc get svc
oc logs deployment/hello-customer
```

The initial build may still be running; check `oc get pods` again before concluding there is an error. For detailed build logs, inspect the build in the web console or run `oc logs build/<actual-build-name>`.

## Step 4 — Expose the app to the customer over HTTPS

When the app is ready and the service `hello-customer` exists:

```powershell
oc create route edge hello-customer --service=hello-customer
oc get route hello-customer
```

Copy the **HOST/PORT** value from `oc get route hello-customer` and open **https://HOSTNAME** in your browser. The exact hostname comes from your cluster; don't reuse a sample hostname. Try `/health` too.

If your OpenShift admin restricts routes, request permission or use the cluster's supported exposure process. A web app on the internet is not protected by authentication just because it is hosted on OpenShift.

## Step 5 — Deliver version 1.0 to the customer

You have two delivery choices:

**A. Hosted/SaaS delivery:** Send the working `https://...` OpenShift Route URL to the customer. They use the software from a browser and install nothing. A Red Hat Developer Sandbox is temporary and unsuitable for real production use; use a paid/managed customer-safe environment before an actual production rollout.

**B. Customer-hosted software:** Create a Git tag marking the tested version and give the customer the Git repository (or an approved release artifact), source code/version, and deployment instructions. The customer's OpenShift administrator runs a deployment in the customer's namespace. For example, with a public demo repository:

```powershell
git tag -a v1.0.0 -m "First customer demo release"
git push origin v1.0.0
```

The customer can deploy the exact source tag with:

```powershell
oc new-app "https://github.com/YOUR_USERNAME/hello-customer.git#v1.0.0" --name=hello-customer
oc create route edge hello-customer --service=hello-customer
```

## Step 6 — Make a change, push, and release again

Edit the text in `wsgi.py`, then:

```powershell
python -m unittest discover -s tests -v
git add wsgi.py
git commit -m "Update customer greeting"
git push
```

The GitHub Actions tests run automatically. **Git push does not automatically redeploy in this project.** After the tests pass, run:

```powershell
oc start-build hello-customer --follow
oc get pods
```

OpenShift fetches the latest source from the configured Git ref, rebuilds it and—when its image-change trigger is configured by `new-app`—rolls out the new application. Refresh the customer URL to verify the change. This is a simple, deliberate *manual release gate* rather than automatic production deployment.

For customer releases, create a new version tag such as `v1.0.1` and document the change. For an improved second project, connect GitHub Actions or OpenShift Pipelines to test/build/deploy automatically after approval.

## Things to observe in the OpenShift dashboard

- **Builds**: code is assembled into a runnable image.
- **ImageStream**: OpenShift records the built image.
- **Pod**: the running application process.
- **Deployment**: controls how many replicas of the app run and handles updates.
- **Service**: provides stable networking within the cluster.
- **Route**: gives the customer an HTTPS address to reach the service.

## Troubleshooting

| Symptom | Check |
|---|---|
| `oc` not recognized | Install OpenShift CLI and reopen PowerShell; inspect PATH. |
| Git push denied | Authenticate to your *own* repo; verify its URL with `git remote -v`. |
| Python builder missing | Use the cluster catalog or explicit approved Python S2I builder. |
| Pod not starting | `oc get pods`, `oc describe pod POD_NAME`, and `oc logs deployment/hello-customer`. |
| Route returns 503 | Check readiness, service endpoints, `oc get pods`, and deployment logs. |
| Code changed but site did not | Check GitHub Actions; manually `oc start-build hello-customer --follow`, then verify new deployment. |
| SSL/certificate error | Check the cluster's default router certificate and chosen hostname with your admin; do not bypass TLS verification for real customers. |

## Source documentation

- Red Hat OpenShift S2I: https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html/building_applications/creating-applications
- Red Hat CLI deployment walkthrough: https://developers.redhat.com/learning/learn%3Aopenshift%3Afoundations-openshift/resource/resources%3Ainstall-application-source-code-using-oc-cli-tool
- Red Hat route command: https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html-single/cli_tools/index
- Red Hat Python S2I images: https://github.com/sclorg/s2i-python-container
- Red Hat free sandbox: https://developers.redhat.com/developer-sandbox
