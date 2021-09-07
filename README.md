
## PIZZA - a task-oriented semantic parsing dataset

The PIZZA dataset continues the exploration of task-oriented parsing by introducing a new dataset for parsing pizza and drink orders, whose semantics cannot be captured by flat slots and intents.

The dataset comes in two main versions, one in a recently introduced utterance-level hierarchical notation that we call TOP, and one whose targets are executable representations (EXR).

Below are two examples of orders that can be found in the data:
```
{
    "dev.SRC": "five medium pizzas with tomatoes and ham",
    "dev.EXR": "(ORDER (PIZZAORDER (NUMBER 5 ) (SIZE MEDIUM ) (TOPPING HAM ) (TOPPING TOMATOES ) ) )",
    "dev.TOP": "(ORDER (PIZZAORDER (NUMBER five ) (SIZE medium ) pizzas with (TOPPING tomatoes ) and (TOPPING ham ) ) )"
}
{
    "dev.SRC": "i want to order two medium pizzas with sausage and black olives and two medium pizzas with pepperoni and extra cheese and three large pizzas with pepperoni and sausage",
    "dev.EXR": "(ORDER (PIZZAORDER (NUMBER 2 ) (SIZE MEDIUM ) (COMPLEX_TOPPING (QUANTITY EXTRA ) (TOPPING CHEESE ) ) (TOPPING PEPPERONI ) ) (PIZZAORDER (NUMBER 2 ) (SIZE MEDIUM ) (TOPPING OLIVES ) (TOPPING SAUSAGE ) ) (PIZZAORDER (NUMBER 3 ) (SIZE LARGE ) (TOPPING PEPPERONI ) (TOPPING SAUSAGE ) ) )",
    "dev.TOP": "(ORDER i want to order (PIZZAORDER (NUMBER two ) (SIZE medium ) pizzas with (TOPPING sausage ) and (TOPPING black olives ) ) and (PIZZAORDER (NUMBER two ) (SIZE medium ) pizzas with (TOPPING pepperoni ) and (COMPLEX_TOPPING (QUANTITY extra ) (TOPPING cheese ) ) ) and (PIZZAORDER (NUMBER three ) (SIZE large ) pizzas with (TOPPING pepperoni ) and (TOPPING sausage ) ) )"
}
```

While more details on the dataset conventions and construction can be found in the paper, we give a high level idea of the main rules our target semantics follow:

- Each order can include any number of pizza and/or drink suborders. These suborders are labeled with the constructors `PIZZAORDER` and `DRINKORDER`, respectively.
- Each top-level order is always labeled with the root constructor `ORDER`.
- Both pizza and drink orders can have `NUMBER` and `SIZE` attributes.
- A pizza order can have any number of `TOPPING` attributes, each of which can be negated. Negative particles can have larger scope with the use of the `or` particle, e.g., `no peppers or onions` will negate both peppers and onions.
- Toppings can be modified by quantifiers such as `a lot` or `extra`, `a little`, etc.
- A pizza order can have a `STYLE` attribute (e.g., `thin crust` style or `chicago` style).
- Styles can be negated.
- Each drink order must have a `DRINKTYPE` (e.g. `coke`), and can also have a `CONTAINERTYPE` (e.g. `bottle`) and/or a `volume` modifier (e.g.,  `three 20 fl ounce coke cans`).

We view `ORDER`, `PIZZAORDER`, and `DRINKORDER` as intents, and the rest of the semantic constructors as composite slots, with the exception of the leaf constructors, which are viewed as entities (resolved slot values).


## Dataset statistics

In the below table we give high level statistics of the data.


|                        | Train | Dev | Test |
|------------------------|-------|-----|------|
| Number of utterances    | 2,456,446 | 348 | 1,357 |
| Unique entities         | 367 | 109 | 180 |
| Avg entities per utterance | 5.32 | 5.37 | 5.42 |
| Avg intents per utterance | 1.76 | 1.25 | 1.28


More details can be found in appendix of our publication.


## Getting Started

The repo structure is as follows:
```
PIZZA
|
|_____ data
|      |_____ PIZZA_train.json.zip             # a zipped version of the training data
|      |_____ PIZZA_train.10_percent.json.zip  # a random subset representing 10% of training data
|      |_____ PIZZA_dev.json                   # the dev portion of the data
|      |_____ PIZZA_test.json                  # the test portion of the data
|
|_____ utils
|      |_____ __init__.py
|      |_____ entity_resolution.py # entity resolution script
|      |_____ express_utils.py     # utilities
|      |_____ semantic_matchers.py # metric functions
|      |_____ sexp_reader.py       # tree reader helper functions 
|      |_____ trees.py             # tree classes and readers
|      |
|      |_____ entities             # directory with entity files
|      
|_____ doc 
|      |_____ PIZZA_dataset_reader_metrics_examples.ipynb
|
|_____ READMED.md

```

The dev and test data files are json lines files where each line represents one utterance and contains 4 keys:
- `*.SRC`: the natural language order input
- `*.EXR`: the ground truth target semantic representation in EXR format
- `*.TOP`: the ground truth target semantic representation in TOP format
- `*.PCFG_ERR`: a boolean flag indicating whether our PCFG system parsed the utterance correctly. See publication for more details

The training data file comes in a similar format, with two differences:
- there is no `train.PCFG_ERR` flag since the training data is all synthetically generated hence parsable with perfect accuracy. In other words, this flag would be `True` for all utterances in that file.
- there is an extra `train.TOP-DECOUPLED` key that is the ground truth target semantic representation in TOP-Decoupled format. See publication for more details.


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the CC-BY-NC-4.0 License.

