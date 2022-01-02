import os
import typing

import click
import faker
import igraph
import pandas as pd
import tqdm
import yaml


def load_schemas(schemas_dir: str) -> typing.Dict[str, typing.Dict]:
    # caveat: the files have to have unique names
    schemas = {}
    for root, dirs, files in os.walk(schemas_dir):
        for f in files:
            basename, ext = os.path.splitext(f)
            if ext in [".yml", ".yaml"]:
                with open(os.path.join(root, f), 'rb') as f:
                    schemas[basename] = yaml.load(f, Loader=yaml.Loader)
    return schemas


def table_order_from_schema(
    schemas: typing.Dict[str, typing.Dict]
) -> (typing.Dict[str, typing.Dict], typing.List[str]):
    g = igraph.Graph(directed=True)
    edges = set()
    all_tables = {}
    # First we need to gather all the vertices
    for schema_name, schema in schemas.items():
        for table in schema["tables"]:
            v = f"{schema_name}.{table['name']}"
            g.add_vertex(name=v)
            for col in table["columns"]:
                if "relationship" in col:
                    to_v = ".".join(
                        col["relationship"]["to"].split(".")[:-1]
                    )  # schema.table.column
                    edges.add((v, to_v))
            all_tables[v] = table
    g.add_edges(list(edges))
    if not g.is_dag():
        raise ValueError(
            "Detected cycle in the graph. Only directed acyclic graphs are supported!"
        )
    return all_tables, [g.vs[v]["name"] for v in g.topological_sorting("in")]


def store_generated_table(
    generated_table: typing.Dict[str, typing.List[typing.Any]],
    table_name: str,
    out_dir: str,
) -> None:
    df = pd.DataFrame.from_dict(generated_table)
    df.to_csv(os.path.join(out_dir, f"{table_name}.csv"), index=False)


def synthesize_data(schemas: typing.Dict[str, typing.Dict], out_dir: str) -> None:
    # Need to make sure that the out dir exists first
    os.makedirs(out_dir, exist_ok=True)
    fake = faker.Faker()
    faker.Faker.seed(0)
    generated = (
        {}
    )  # column store, might think of a more scalable solution in the future
    # We need to do a topological sort to determine the order in which we should generate the data
    all_tables, sorted_tables = table_order_from_schema(schemas)
    for t in tqdm.tqdm(sorted_tables):
        for col in all_tables[t]["columns"]:
            if "relationship" in col:
                if col["relationship"]["kind"] == "1-1":
                    # we cannot allow repetitions
                    generated[f"{t}.{col['name']}"] = fake.random.sample(
                        generated[col["relationship"]["to"]], all_tables[t]["size"]
                    )
                elif col["relationship"]["kind"] == "1-many":
                    # allow repetitions
                    generated[f"{t}.{col['name']}"] = fake.random_choices(
                        generated[col["relationship"]["to"]], all_tables[t]["size"]
                    )
            elif "formatter" in col:
                formatter = fake.get_formatter(col["formatter"])
                if col.get("unique", False):
                    vals = set()
                    while len(vals) < all_tables[t]["size"]:
                        vals.add(
                            formatter(*col.get("args", []), **col.get("kwargs", {}))
                        )
                    generated[f"{t}.{col['name']}"] = list(vals)
                else:
                    generated[f"{t}.{col['name']}"] = [
                        formatter(*col.get("args", []), **col.get("kwargs", {}))
                        for _ in range(all_tables[t]["size"])
                    ]
        store_generated_table(
            {
                col["name"]: generated[f"{t}.{col['name']}"]
                for col in all_tables[t]["columns"]
            },
            t,
            out_dir,
        )


@click.command()
@click.option(
    "--schemas-dir",
    default="../example",
    help="Path to the directory with schemas to use when generating",
)
@click.option(
    "--out-dir",
    default="../out",
    help="Path to the directory where you want to generate your files",
)
def main(schemas_dir, out_dir):
    schemas = load_schemas(schemas_dir)
    synthesize_data(schemas, out_dir)


if __name__ == "__main__":
    main()
