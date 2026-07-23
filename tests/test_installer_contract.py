import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class InstallerContractTests(unittest.TestCase):
    def test_shell_installer_is_a_native_bootstrap(self):
        installer = (ROOT / "scripts/install-turbo.sh").read_text()
        self.assertIn('workflow add', installer)
        self.assertIn('bundle install speckit-turbo', installer)
        self.assertNotIn('"$SPECIFY_BIN" workflow update', installer)
        self.assertIn('extension add turbo --force', installer)
        self.assertNotIn("git clone", installer)
        self.assertNotIn("node_modules", installer)

    def test_powershell_installer_exists(self):
        installer = ROOT / "scripts/Install-Turbo.ps1"
        self.assertTrue(installer.is_file())
        text = installer.read_text()
        self.assertIn("specify bundle install speckit-turbo", text)
        self.assertIn("Get-Content -Raw", text)
        self.assertNotIn("Select-String", text)
        self.assertNotIn("& specify workflow update", text)
        self.assertIn("extension add turbo --force", text)


if __name__ == "__main__":
    unittest.main()
