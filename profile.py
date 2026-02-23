import geni.portal as portal
import geni.rspec.pg as rspec

pc = portal.Context()
request = pc.makeRequestRSpec()

# -------- Parameters you can edit in the CloudLab UI --------
pc.defineParameter("REPO", "Git repo URL", portal.ParameterType.STRING,
                   "https://github.com/harvard-cns/teal.git")
pc.defineParameter("BRANCH", "Git branch", portal.ParameterType.STRING, "main")
pc.defineParameter("NODETYPE", "Hardware type", portal.ParameterType.STRING, "YOUR_GPU_NODETYPE")
pc.defineParameter("IMAGE", "Disk image URN", portal.ParameterType.STRING,
                   "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD")
params = pc.bindParameters()
# ------------------------------------------------------------

node = request.RawPC("n0")
node.hardware_type = params.NODETYPE
node.disk_image = params.IMAGE

node.addService(rspec.Execute(shell="bash", command=f"""
set -euxo pipefail

sudo mkdir -p /local/logs
sudo chown -R $USER:$USER /local/logs || true

exec > >(tee -a /local/logs/profile_bootstrap.log) 2>&1

sudo apt-get update -y
sudo apt-get install -y git

cd /local
if [ ! -d teal ]; then
  git clone "{params.REPO}" teal
fi

cd /local/teal
git fetch --all --prune
git checkout "{params.BRANCH}" || git checkout -b "{params.BRANCH}" "origin/{params.BRANCH}"
git pull || true

chmod +x startup.sh || true
# run startup (keep it idempotent)
sudo -E bash ./startup.sh
"""))

pc.printRequestRSpec(request)