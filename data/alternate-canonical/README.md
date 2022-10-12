# Data Augmentation for Semantic Parsing

This repo contains the updated canonical forms dataset for [PIZZA](https://github.com/amazon-research/pizza-semantic-parsing-dataset) (Original Canonical Forms [here](https://github.com/amazon-research/resource-constrained-naturalized-semantic-parsing)) used in the paper, CLASP: Few-Shot Cross-Lingual Data Augmentation for Semantic Parsing. (TODO: link to arXiv).

# Getting started
The alternate files are an augmentation of the original dataset in `pizza-semantic-parsing-dataset/data` where the "canonical form" - referred to as CF - format is provided for each utterance.

There are five files:

* `PIZZA_dev.16_shots.json` contains a subset of 16 samples from the `dev` set, the same subset used by [Rongali et. al. 2022](https://github.com/amazon-research/resource-constrained-naturalized-semantic-parsing).
* `PIZZA_dev.json` contains the 348 human annotated `dev` samples.
* `PIZZA_test.json` contains the 1357 human annotated `test` samples.
* `PIZZA_train.subsets.json.zip` is a zip file containing 3 subsets of the training data: `PIZZA_train.348_shots.json`, `PIZZA_train.3480_shots.json`, `PIZZA_train.104400_shots.json`, containing 348, 3,480, and 104,400 samples, respectively. Please see the CLASP paper for details about how each subset is used.
* `PIZZA_train_unshuffled.json` is a zip file containing the full 2M training dataset with canonical forms. It has only SRC and CF to reduce file footprint, as the other fields TOP, TOP-Decoupled and EXR can be found in the original training file in `pizza-semantic-parsing-dataset/data`.

Each json file contains four fields, where `XXX` is either `train`, `dev`, or `test`.

* `XXX.SRC`: The input source text.
* `XXX.CF`: The (alternate) Canonical Form target.
* `XXX.EXR`: The EXR field from the original PIZZA dataset.
* `XXX.TOP`: The TOP field from the original PIZZA dataset.



# Cite

TODO: bibtex citation goes here.

# License

This library is licensed under the CC-BY-NC-4.0 License.

TODO: add license file to this repo.
