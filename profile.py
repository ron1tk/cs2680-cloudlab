import geni.portal as portal
import geni.rspec.pg as pg

pc = portal.Context()

# -------- Parameters shown in CloudLab UI --------
pc.defineParameter("REPO", "Git repo URL", portal.ParameterType.STRING,
                   "https://github.com/harvard-cns/teal.git")
pc.defineParameter("BRANCH", "Git branch", portal.ParameterType.STRING, "main")
pc.defineParameter("NODETYPE", "Hardware type", portal.ParameterType.STRING, "c4130",
                   [("c4130", "GPU (NVIDIA)"),
                    ("c240g5", "CPU-only (no GPU)"),
                    ("c6525-25g", "25G Mellanox (CPU-only)")])
pc.defineParameter("IMAGE", "Disk image URN", portal.ParameterType.STRING,
                   "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD")
params = pc.bindParameters()
# ------------------------------------------------

request = pc.makeRequestRSpec()

node = request.RawPC("n0")
node.hardware_type = params.NODETYPE
node.disk_image = params.IMAGE

cmd = """
set -euxo pipefail

sudo mkdir -p /local/logs
sudo chown -R $USER:$USER /local/logs || true
exec > >(tee -a /local/logs/profile_bootstrap.log) 2>&1

sudo apt-get update -y
sudo apt-get install -y git

cd /local
if [ ! -d teal ]; then
  git clone "{REPO}" teal
fi

cd /local/teal
git fetch --all --prune
git checkout "{BRANCH}" || git checkout -b "{BRANCH}" "origin/{BRANCH}"
git pull || true

chmod +x startup.sh || true
sudo -E bash ./startup.sh
""".format(REPO=params.REPO, BRANCH=params.BRANCH)

node.addService(pg.Execute(shell="bash", command=cmd))

pc.printRequestRSpec(request)