<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
  <img src="assets/hero-light.svg" alt="David Padilla Orenga — freelance engineer in computer vision, AI, robotics and automation" width="100%">
</picture>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-David_Padilla_Orenga-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/david-padilla-orenga-7a232a134/)
[![sfmkit](https://img.shields.io/badge/sfmkit-Structure_from_Motion-FF5A1F?style=for-the-badge&labelColor=0A0A0A)](https://github.com/dpadillaor/sfmkit)
![Valencia](https://img.shields.io/badge/Valencia-🇪🇸_remote-C9CBD1?style=for-the-badge&labelColor=0A0A0A)

![Profile views](https://komarev.com/ghpvc/?username=dpadillaor&style=flat-square&color=FF5A1F&label=profile+views)
&nbsp;![Followers](https://img.shields.io/github/followers/dpadillaor?style=flat-square&color=FF5A1F&labelColor=0A0A0A)

</div>

Engineer working where **computer vision, AI, robotics and automation** meet. I take systems that look great on a
benchmark and make them hold up in the real world: on a moving camera, in a hospital dataset, on a client's hardware,
inside a company's daily processes. Find what breaks, replace it with something better, measure it.

---

## 🧭 What I actually do

```
Computer vision  ──►  Detection, segmentation and multi-object tracking that survive *your* camera
3D & SLAM        ──►  Reconstruction, localization, place recognition, open-vocabulary 3D maps
Robotics         ──►  Perception a robot can use: persistent instances you can query in plain language
AI / ML          ──►  Datasets, training, fine-tuning and evaluation that is honest about failure cases
Automation       ──►  LLM agents and workflows for companies, with a human in the loop and a log of everything
```

```mermaid
flowchart LR
  CAM(["camera · video<br/>RGB-D · documents"]) --> PER{{"perception<br/>YOLO · SAM · CLIP"}}
  PER --> TRK["tracking<br/>who moved where"]
  PER --> MAP["3D map<br/>SLAM · SfM · instances"]
  PER --> DOC["understanding<br/>LLM extraction"]
  TRK --> OUT["metrics<br/>and reports"]
  MAP --> OUT
  MAP --> ROB["robot<br/>queries the scene"]
  DOC --> AGT["agents<br/>and workflows"]
  AGT --> OUT
  OUT --> PROD(["in production<br/>measured on your hardware"])
  ROB --> PROD

  classDef src fill:#FF5A1F,stroke:#C23D0C,stroke-width:2px,color:#FFFFFF
  classDef core fill:#0A0A0A,stroke:#0A0A0A,color:#FFFFFF
  classDef mid fill:#FFE3D7,stroke:#FF5A1F,color:#0A0A0A
  class CAM,PROD src
  class PER core
  class TRK,MAP,DOC,ROB,AGT,OUT mid
```

---

## 🔭 Selected work

<table>
<tr>
<td width="52%" valign="top">
<a href="https://github.com/dpadillaor/sfmkit"><img src="assets/sfmkit-visor.png" alt="sfmkit viewer: point cloud of Valencia's Plaza de la Virgen, my reconstruction in orange and COLMAP's in blue, with the cameras of fourteen photos and the old photograph" width="100%"></a>
</td>
<td width="48%" valign="top">

**[sfmkit](https://github.com/dpadillaor/sfmkit)** &nbsp;<sub>`OPEN SOURCE`</sub>

*Where was this century-old photograph taken from, and what has changed since?*

Structure from Motion written from the geometry up, with my own bundle adjustment. From **14 phone photos** of
Valencia's Plaza de la Virgen it rebuilds the square within **0.30° of COLMAP**, places an undated old photograph in the
model and flags what changed. Ships with a live 3D viewer.

`Python` `NumPy` `SuperPoint` `LightGlue` `COLMAP` `three.js`

[Code](https://github.com/dpadillaor/sfmkit) · [Docs](https://dpadillaor.github.io/sfmkit/)

</td>
</tr>
</table>

| Project | What I did | Stack |
|---|---|---|
| **3D instances that survive loop closure** <br><sub>MSc thesis · [OVO](https://github.com/dpadillaor/OVO)</sub> | Open-vocabulary online 3D mapping lost its object merges after loop closure. Traced it to stale geometry; added local bundle adjustment, a point-ownership conflict system that merges and splits instances from temporal evidence, and a better fusion step. | `CLIP` `SAM 2` `ORB-SLAM2` `Gaussian-SLAM` `Rerun` |
| **Learned place recognition for colonoscopy SLAM** <br><sub>Research internship · University of Zaragoza</sub> | Replaced Bag of Words in CudaSIFT-SLAM with ColonMapper, a learned global descriptor, ported to C++. Real time in loop closure and map merging; matches BoW and beats it on some sequences. | `C++` `LibTorch` `OpenCV` `C3VD` |
| **Scouting metrics from match video** <br><sub>Client · sports analytics</sub> | Football tracker that detects and follows players in match footage to extract scouting metrics. | `Detection` `MOT` `Video` |
| **Digitising an engineering firm** <br><sub>Client · automation</sub> | A database where there was none, automated processes and email, agents for repetitive work, a desktop app for energy-certification workflows and a Flutter app for on-site capture. | `Python` `Flutter` `LLM agents` `n8n` |
| **Water-meter digital twin** <br><sub>Public sector</sub> | Remote-reading platform for a town's LoRaWAN water meters: consumption, alarms and the state of every meter. | `TypeScript` `LoRaWAN` |
| [`catastro-scraper`](https://github.com/dpadillaor/catastro-scraper) | Retrieves PDF certificates and location maps from the Spanish Cadastre. | `Python` |
| [`Sem3_SI_ImageEmbedding`](https://github.com/dpadillaor/Sem3_SI_ImageEmbedding) | Seminar on CLIP-based image embeddings and retrieval. | `CLIP` `Jupyter` |

> 🔒 Most client work lives in private repos. Happy to walk through it on a call.

---

## 🎓 Path

```mermaid
%%{init: {"themeVariables": {"cScale0": "#0A0A0A", "cScaleLabel0": "#FFFFFF", "cScale1": "#565656", "cScaleLabel1": "#FFFFFF", "cScale2": "#FF8A5B", "cScaleLabel2": "#0A0A0A", "cScale3": "#FF5A1F", "cScaleLabel3": "#FFFFFF"}}}%%
timeline
    title Mechanics, then simulation, then machines that see
    Engineering : BEng Industrial Engineering · Universitat Jaume I
        : Mechanical engineering & mechatronics · INSA Lyon
        : MSc Industrial Engineering
    Simulation : A long run building and validating simulations
    Vision, AI & robotics : MSc Computer Vision, AI & Robotics
        : Research internship in endoscopy SLAM · University of Zaragoza
        : Thesis on open-vocabulary 3D mapping
    Freelance : Vision, 3D and automation for clients
        : Open source · sfmkit
```

🇪🇸 Spanish · 🇬🇧 English · 🇫🇷 French

---

## 🛠️ Toolbox

<div align="center">

**Languages**

[![Languages](https://skillicons.dev/icons?i=py,cpp,rust,ts,dart,bash&theme=dark)](https://skillicons.dev)

**Vision, AI & 3D**

[![AI](https://skillicons.dev/icons?i=pytorch,opencv,threejs&theme=dark)](https://skillicons.dev)

**Apps & infra**

[![Infra](https://skillicons.dev/icons?i=flutter,astro,tailwind,docker,redis,sqlite,linux,git&theme=dark)](https://skillicons.dev)

`CUDA` · `LibTorch` · `SAM 2/3` · `CLIP` · `SigLIP` · `YOLO` · `COLMAP` · `Gaussian Splatting` · `Rerun` · `n8n` · `Claude Code`

</div>

---

## 📊 Activity

<div align="center">

<img width="49%" src="https://github-profile-summary-cards.vercel.app/api/cards/stats?username=dpadillaor&theme=transparent" alt="GitHub stats">
<img width="49%" src="https://github-profile-summary-cards.vercel.app/api/cards/repos-per-language?username=dpadillaor&theme=transparent" alt="Repos per language">

<img width="62%" src="https://streak-stats.demolab.com?user=dpadillaor&hide_border=true&background=00000000&ring=FF5A1F&fire=FF5A1F&currStreakLabel=FF5A1F&sideLabels=8B949E&dates=8B949E&currStreakNum=8B949E&sideNums=8B949E&stroke=8B949E" alt="Contribution streak">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/dpadillaor/dpadillaor/output-3d/profile-3d-dark.svg">
  <img alt="3D contribution calendar" src="https://raw.githubusercontent.com/dpadillaor/dpadillaor/output-3d/profile-3d-light.svg" width="100%">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/dpadillaor/dpadillaor/output/snake-dark.svg">
  <img alt="A snake eating my contribution graph" src="https://raw.githubusercontent.com/dpadillaor/dpadillaor/output/snake-light.svg" width="100%">
</picture>

</div>

---

## 🤝 Let's talk

A camera that should be counting something, a robot that needs to understand its surroundings, a 3D capture to turn
into something useful, or a company drowning in manual work between its tools: that is my favourite kind of conversation.
**First I tell you whether it's viable. Then I build it.**

<div align="center">

[![LinkedIn](https://img.shields.io/badge/Connect_on_LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/david-padilla-orenga-7a232a134/)
[![sfmkit](https://img.shields.io/badge/See_sfmkit-FF5A1F?style=for-the-badge&labelColor=0A0A0A&logo=github&logoColor=white)](https://github.com/dpadillaor/sfmkit)

</div>
