import argparse
import os
from pathlib import Path

import numpy as np
from joblib import dump
from sklearn.cluster import KMeans, MiniBatchKMeans


def train_kmeans(features, args):
    if not args.batched:
        model = KMeans(
            n_clusters=args.n_clusters,
            n_init=args.n_init,
            max_iter=args.max_iter,
            verbose=args.verbose,
            random_state=args.random_state,
            copy_x=False,
        )
    else:
        model = MiniBatchKMeans(
            n_clusters=args.n_clusters,
            compute_labels=True,
            max_iter=args.max_iter,
            batch_size=args.batch_size,
            verbose=args.verbose,
            random_state=args.random_state,
            max_no_improvement=10,
            n_init=args.n_init,
        )
    model = model.fit(features)
    return model


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--embedded-dataset-path",
        type=str,
        help="Path to the file with sentence representations",
    )
    parser.add_argument(
        "--out-file-model", type=str, help="Path to file to save kmeans model"
    )
    parser.add_argument(
        "--out-file-labels",
        type=str,
        help="Path to file to save cluster labels for dataset",
    )
    parser.add_argument(
        "--n-clusters", type=int, default=8, help="Number of clusters of k-means"
    )
    parser.add_argument(
        "--n_init", type=int, default=10, help="Number of random restarts of k-means"
    )
    parser.add_argument(
        "--max-iter",
        type=int,
        default=300,
        help="Maximum number of iterations of the k-means algorithm for a single run.",
    )
    parser.add_argument(
        "--batched",
        type=bool,
        default=False,
        help="Either to run batched k-means model",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1024,
        help="Batch size to train k-means if batched",
    )
    parser.add_argument(
        "--max-no-improvement-size",
        type=int,
        default=10,
        help="Patience for batched kmneas",
    )
    parser.add_argument(
        "--verbose", type=int, default=0, help="Random state for intializations"
    )
    parser.add_argument(
        "--random-state", type=int, default=42, help="Random state for intializations"
    )
    args = parser.parse_args()

    features = np.load(args.embedded_dataset_path)["arr_0"]
    model = train_kmeans(features=features, args=args)

    Path(os.path.dirname(args.out_file_model)).mkdir(parents=True, exist_ok=True)
    dump(model, args.out_file_model)
    print(f"Saved model to {args.out_file_model}")

    Path(os.path.dirname(args.out_file_labels)).mkdir(parents=True, exist_ok=True)
    np.savetxt(args.out_file_labels, model.labels_, fmt="%i")
    print(f"Saved labels to {args.out_file_labels}")
