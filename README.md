# Sensor Suite (Autotest & libreVNA)

This repository is a packaged snapshot of the `Autotest_loading` automation script and the `libreVNA` helper used in my sensor measurement workflows.

Contents
- `src/Autotest_loading.py` — automated loading test scripts for force sensors and VNA integration.
- `src/libreVNA.py` — lightweight TCP client for communicating with LibreVNA-GUI's TCP server.

Usage
1. Replace each `YOUR_PATH`, `YOUR_*_COM_PORT`, and `YOUR_VNA_HOST` placeholder in `src/Autotest_loading.py` with your local configuration.
2. Install the Python dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

3. The script expects LibreVNA-GUI with its TCP server enabled (default port 19542), a calibration CSV, and serial devices for the motor, force sensor, and trigger. Configure the placeholders before running.

Safety
- `Autotest_loading.py` can command physical motor movement and force-sensor operations. Review the procedure and test with appropriate safeguards before connecting hardware.

Notes & Caution
- The machine-specific paths, COM port assignments, and VNA host identifier have been replaced with placeholders in this repository copy. The original local scripts were not modified.
- Review the protocol frames, calibration method, device commands, project terminology, and any company-owned implementation with the relevant rights holder before making the repository public. A local scan cannot determine ownership or confidentiality.

Suggested next steps
- Review and sanitize the code for confidential information.
- Add a concise `README.md` explanation for key scripts and minimal reproduction steps.
- Add tests/CI and a short demo (screenshot or GIF) to improve the repository's value on GitHub.

License
No license has been selected. Confirm that you have the right to publish this code and choose a license before public release; without a license, others do not receive permission to reuse it.
