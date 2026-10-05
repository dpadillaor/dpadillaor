<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/header-dark.svg">
  <img alt="David Padilla Orenga — Computer Vision · AI · Robotics · Automation" src="assets/header-light.svg" width="100%">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/ribbon-dark.svg">
  <img alt="Computer Vision · SLAM · Structure from Motion · PyTorch · CUDA · C++ · Python · Rust · LLM agents · automation" src="assets/ribbon-light.svg" width="100%">
</picture>

<br>

I'm **David**, a freelance engineer working across **computer vision, AI, robotics and automation**. Industrial and mechatronics engineer by training, with a master's in **computer vision, AI & robotics** and a long background in simulation before that. One idea runs through everything I build: **it has to work in real conditions, not just on the benchmark.**

From a 3D map that a robot can query in plain language to the agent that sorts a company's email, the job is the same: find what breaks outside the lab, replace it with something better, and measure it.

<br>

## `01` &nbsp;What I do

<table>
<tr>
<td width="50%" valign="top">

**`VIDEO` &nbsp;Detection & tracking**<br>
Counting, inspecting or following things when off-the-shelf models fail on *your* camera. Fine-tuned to your data, measured on your hardware.

</td>
<td width="50%" valign="top">

**`ROBOTICS` &nbsp;Semantic 3D understanding**<br>
Persistent object instances and open vocabulary: ask the map in natural language, no retraining.

</td>
</tr>
<tr>
<td valign="top">

**`SLAM` &nbsp;Robust localization**<br>
Low texture, reflections, abrupt motion. I swap the module that fails and benchmark it against the original.

</td>
<td valign="top">

**`CAPTURE` &nbsp;3D reconstruction**<br>
Point cloud, mesh or Gaussian splat, with calibrated cameras and a viewer to show it — from capture onwards.

</td>
</tr>
<tr>
<td valign="top">

**`MODELS` &nbsp;Custom machine learning**<br>
When no catalogue model answers your question: dataset, training or fine-tuning, and an honest evaluation.

</td>
<td valign="top">

**`PROCESS` &nbsp;AI automation for companies**<br>
Reading documents, triaging email, moving data. Workflows and LLM agents with a human in the loop and a log of what they did.

</td>
</tr>
<tr>
<td colspan="2" valign="top">

**`ASSETS` &nbsp;Digital twins** — every asset, where it is and what it reports, kept up to date with real data instead of scattered spreadsheets.

</td>
</tr>
</table>

<br>

## `02` &nbsp;Selected work

<table>
<tr>
<td width="55%" valign="top">
<a href="https://github.com/dpadillaor/sfmkit"><img src="assets/sfmkit-visor.png" alt="sfmkit viewer: point cloud of Valencia's Plaza de la Virgen, my reconstruction in orange and COLMAP's in blue, with the cameras of fourteen photos and the old photograph" width="100%"></a>
</td>
<td width="45%" valign="top">

<sub>`OPEN SOURCE` · `STRUCTURE FROM MOTION`</sub>

### [sfmkit](https://github.com/dpadillaor/sfmkit)

Structure from Motion written from the geometry up: matching, incremental reconstruction and my own bundle adjustment. From **14 phone photos** of Valencia's Plaza de la Virgen it rebuilds the square within **0.30° of COLMAP**, locates an undated century-old photograph in the model and flags what has changed since.

`Python` `NumPy` `SuperPoint` `LightGlue` `COLMAP` `three.js` `Docker`

[Code](https://github.com/dpadillaor/sfmkit) · [Docs](https://dpadillaor.github.io/sfmkit/)

</td>
</tr>
</table>

<table>
<tr>
<td width="50%" valign="top">

<sub>`MSC THESIS` · `OPEN-VOCABULARY 3D`</sub>

#### 3D instances that survive loop closure

[OVO](https://github.com/dpadillaor/OVO) builds, while the camera moves, a 3D map where every object is an instance you can query with text. After a loop closure, instances stopped merging correctly. I traced it to stale geometry and fixed it with **local bundle adjustment**, a **point-ownership conflict system** that merges and splits instances from accumulated temporal evidence, and an improved fusion step.

`CLIP` `SAM 2` `ORB-SLAM2` `Gaussian-SLAM` `Rerun`

</td>
<td width="50%" valign="top">

<sub>`RESEARCH INTERNSHIP` · `UNIVERSITY OF ZARAGOZA`</sub>

#### Learned place recognition in colonoscopy SLAM

In CudaSIFT-SLAM, a SLAM system for colonoscopy, I replaced Bag-of-Words place recognition with **ColonMapper**, a learned global descriptor. Ported to C++, it runs in **real time** for loop closure and map merging, matches Bag of Words and beats it on some sequences.

`C++` `LibTorch` `TorchScript` `OpenCV` `C3VD`

</td>
</tr>
<tr>
<td valign="top">

<sub>`CLIENT` · `SPORTS ANALYTICS`</sub>

#### Scouting metrics from match video

A football tracker that detects and follows players in broadcast footage to extract metrics useful for scouting.

`Detection` `Multi-object tracking` `Video`

</td>
<td valign="top">

<sub>`CLIENT` · `AUTOMATION`</sub>

#### Digitising an engineering firm, process by process

A database where there was none, manual processes automated, email handled, and agents for the repetitive work — plus a desktop app for energy-certification workflows and a Flutter app for on-site data capture.

`Python` `Flutter` `LLM agents` `n8n` `Notion API`

</td>
</tr>
<tr>
<td valign="top">

<sub>`PUBLIC SECTOR` · `DIGITAL TWIN`</sub>

#### Water-meter network for a municipality

Web platform for remote reading of a town's LoRaWAN water meters: consumption, alarms and the state of every meter in one place.

`TypeScript` `LoRaWAN` `Data pipelines`

</td>
<td valign="top">

<sub>`TOOLS`</sub>

#### Smaller things

- [**catastro-scraper**](https://github.com/dpadillaor/catastro-scraper) — retrieves PDF certificates and location maps from the Spanish Cadastre.
- [**Image embeddings with CLIP**](https://github.com/dpadillaor/Sem3_SI_ImageEmbedding) — seminar notebooks on CLIP-based retrieval.

</td>
</tr>
</table>

<br>

## `03` &nbsp;Toolbox

| Area | Tools |
|---|---|
| **Vision & 3D** | `YOLO` `SAM 2 / SAM 3` `CLIP` `SigLIP` `Perception Encoder` `OpenCV` `SuperPoint` `LightGlue` `COLMAP` `Gaussian Splatting` |
| **SLAM & geometry** | `ORB-SLAM2` `Gaussian-SLAM` `Bundle Adjustment` `Loop Closure` `Place recognition` `Structure from Motion` |
| **Machine learning** | `PyTorch` `LibTorch` `TorchScript` `CUDA` `NumPy` `Jupyter` |
| **Automation & AI agents** | `LLM agents` `Claude Code` `n8n` `Notion API` `Streamlit` |
| **Languages** | `Python` `C++` `Rust` `TypeScript` `Dart` |
| **Product & infra** | `Flutter` `Astro` `three.js` `Docker` `Redis` `SQLAlchemy` `Git` |
| **Visualisation** | `Rerun` `three.js` `PyVista` `Manim` |

<p>
  <img src="https://img.shields.io/badge/Python-0a0a0a?style=flat-square&logo=python&logoColor=ff5a1f" alt="Python">
  <img src="https://img.shields.io/badge/C++-0a0a0a?style=flat-square&logo=cplusplus&logoColor=ff5a1f" alt="C++">
  <img src="https://img.shields.io/badge/Rust-0a0a0a?style=flat-square&logo=rust&logoColor=ff5a1f" alt="Rust">
  <img src="https://img.shields.io/badge/TypeScript-0a0a0a?style=flat-square&logo=typescript&logoColor=ff5a1f" alt="TypeScript">
  <img src="https://img.shields.io/badge/PyTorch-0a0a0a?style=flat-square&logo=pytorch&logoColor=ff5a1f" alt="PyTorch">
  <img src="https://img.shields.io/badge/CUDA-0a0a0a?style=flat-square&logo=nvidia&logoColor=ff5a1f" alt="CUDA">
  <img src="https://img.shields.io/badge/OpenCV-0a0a0a?style=flat-square&logo=opencv&logoColor=ff5a1f" alt="OpenCV">
  <img src="https://img.shields.io/badge/Flutter-0a0a0a?style=flat-square&logo=flutter&logoColor=ff5a1f" alt="Flutter">
  <img src="https://img.shields.io/badge/Docker-0a0a0a?style=flat-square&logo=docker&logoColor=ff5a1f" alt="Docker">
  <img src="https://img.shields.io/badge/three.js-0a0a0a?style=flat-square&logo=threedotjs&logoColor=ff5a1f" alt="three.js">
  <img src="https://img.shields.io/badge/n8n-0a0a0a?style=flat-square&logo=n8n&logoColor=ff5a1f" alt="n8n">
</p>

<br>

## `04` &nbsp;How I work

> **First I tell you whether it's viable. Then I build it.**

| # | Step | Terms |
|:-:|---|---|
| `1` | **20-minute call** — you tell me the problem; I tell you whether vision or AI is the right path, or if something cheaper will do. | <sub>free</sub> |
| `2` | **Feasibility test** — a scoped prototype on your real data, with numbers and a clear report of what works. | <sub>fixed scope & price</sub> |
| `3` | **Development** — the full system, measured on your hardware, with short demos every week. | <sub>weekly deliveries</sub> |
| `4` | **Handover** — code, documentation, a video of how it works and a session so your team can maintain it. | <sub>yours, no lock-in</sub> |

<br>

## `05` &nbsp;Background

- **MSc in Computer Vision, Artificial Intelligence & Robotics**
- **MSc in Industrial Engineering**
- **BEng in Industrial Engineering** — Universitat Jaume I, Castellón
- **Mechanical engineering & mechatronics** — INSA Lyon
- **Research internship** in SLAM for endoscopy — University of Zaragoza
- 🇪🇸 Spanish · 🇬🇧 English · 🇫🇷 French

<br>

## `06` &nbsp;Let's talk

Got a vision, 3D, robotics or automation problem? Tell me about it — I'll say whether I can help, and if not, who can.

<a href="https://www.linkedin.com/in/david-padilla-orenga-7a232a134/"><img src="https://img.shields.io/badge/LinkedIn-0a0a0a?style=for-the-badge&logo=linkedin&logoColor=ff5a1f" alt="LinkedIn"></a>
<a href="https://github.com/dpadillaor"><img src="https://img.shields.io/badge/GitHub-0a0a0a?style=for-the-badge&logo=github&logoColor=ff5a1f" alt="GitHub"></a>

<br>

<p align="right"><sub><code>VALENCIA · REMOTE</code> &nbsp;·&nbsp; assets generated by <a href="scripts/build_assets.py"><code>scripts/build_assets.py</code></a></sub></p>
