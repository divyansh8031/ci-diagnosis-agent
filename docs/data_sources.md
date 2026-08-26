# External CI Data Sources and Research References

## Important distinction

The current P0/P2/P3 experiment is a **controlled simulation**. The 120 cases per seed were generated from the project's assumed priors and likelihoods. No external dataset was used to generate those cases or to claim empirical calibration.

The datasets below are included as **credible external data sources for future calibration, validation, and extension**, not as evidence that the current simulation probabilities are production frequencies.

## 1. TravisTorrent

**Beller, M., Gousios, G., & Zaidman, A. (2017). _TravisTorrent: Synthesizing Travis CI and GitHub for Full-Stack Research on Continuous Integration._ MSR 2017. DOI: 10.1109/MSR.2017.24.**

TravisTorrent combines Travis CI build information with GitHub repository metadata and provides a large public corpus of CI builds. The published description reports 2,640,825 Travis builds from more than 1,000 projects.

- Research page: https://research.tudelft.nl/en/publications/travistorrent-synthesizing-travis-ci-and-github-for-full-stack-re/
- Dataset: https://travistorrent.testroots.org/
- DOI: https://doi.org/10.1109/MSR.2017.24

**Potential use in this project:** estimate empirical build/failure patterns, study commit history and build outcomes, and investigate whether prior probabilities or historical evidence features can be calibrated.

## 2. UniLoc build-fix dataset

**UniLoc: Unified Fault Localization of Continuous Integration Failures.**

UniLoc provides a dataset of 700 CI/CD build failures and corresponding fixes, extending TravisTorrent. The records link a build-failing commit, subsequent failed builds, and the commit that fixed the failure.

- Dataset/project page: https://sites.google.com/view/uniloc

**Potential use in this project:** this is particularly relevant to the code-regression/failure-localization hypothesis because it links failure-introducing and failure-fixing changes.

## 3. CI-Datasets / Rails Dataset

**Liang, J., Elbaum, S., & Rothermel, G. (2018). _The Rails Dataset of Testing Results from Travis CI._**

The CI-Datasets repository provides test-execution data from Travis CI. The Rails dataset contains thousands of builds and millions of test-suite execution records, including build/job/test-suite outcomes and execution metadata.

- Repository: https://github.com/elbaum/CI-Datasets

**Potential use in this project:** validate rerun/test-history evidence and investigate flaky or repeated test behavior.

## 4. Continuous Defect Prediction dataset

**Madeyski, L. & Kawalerowicz, M. (2017). _Continuous Defect Prediction: The Idea and a Related Dataset._**

This dataset extends TravisTorrent with file-level changes and software-process metrics. The published description reports more than 11 million rows covering 1,265 projects.

- Paper/dataset description: https://arxiv.org/abs/1703.04142

**Potential use in this project:** investigate code-change/history features for the code-regression hypothesis and future historical-aware policy work.

## How these sources relate to our current model

| Current model component | External data that could eventually inform it |
|---|---|
| Prior probability of code regression | TravisTorrent / Continuous Defect Prediction / UniLoc |
| Flaky-test likelihood | CI-Datasets / Rails dataset and dedicated flaky-test datasets |
| Historical evidence | TravisTorrent / Continuous Defect Prediction |
| Failure-introducing changes | UniLoc |
| Rerun/test execution behavior | CI-Datasets / Rails dataset |
| Action/decision costs | **Not directly supplied by these datasets**; requires workflow or practitioner measurement |

## Why we are not using these datasets in the current experiment

Using an external dataset would require defining an explicit mapping from real CI observations to our six hidden states and from real observations to the binary likelihood model. We have not completed that calibration. Claiming that the current 0.40/0.30/0.10/0.10/0.05/0.05 priors or 0.8/0.4/0.1 likelihoods were learned from these datasets would therefore be incorrect.

The correct next research step is:

```text
External labeled CI data
        ↓
Define/validate failure taxonomy
        ↓
Estimate priors and likelihoods
        ↓
Calibrate model
        ↓
Run P0/P2/P3 on held-out real cases
        ↓
Compare simulation vs empirical results
```
