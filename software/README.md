# Software

Host-side code — everything that runs on a PC rather than on the machine. Embedded targets are in
[`firmware/`](../firmware/).

| Project | Role |
| --- | --- |
| [`identification`](identification/) | Torque excitation, acquisition and ODrive servo identification. Two workflows and the waveform generator. |
| [`measurement-tools`](measurement-tools/) | Build and verify [`measurement/data-index.csv`](../measurement/data-index.csv), the manifest indexing measurement data held on Google Drive. |

```bash
pip install -e software/identification
pip install -e software/measurement-tools
```

FRF estimation itself is done by [`refaqt/cnc-frf-estimation`](https://github.com/refaqt/cnc-frf-estimation),
a separate tool; its outputs are the `derived` rows in the measurement manifest.
