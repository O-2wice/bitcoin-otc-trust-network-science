"""Compare the observed network with theoretical expectations from the course models.

Run from the project root after the earlier analyses: python scripts/theory_comparison.py

1. Formula predictions for ER and BA against simulations and the observed network.
2. Power-law tail fits: lower cutoff, uncertainty, goodness of fit, and alternatives.
3. An attachment exponent from event-level recipient choices under several benchmarks.
4. The Molloy-Reed percolation threshold against simulated node removal.
It also checks the sampled path length and sampled betweenness against exact values.
These are descriptive comparisons; none of them identifies a causal mechanism.
"""

from collections import deque
import json
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy import optimize, sparse, special, stats
from scipy.sparse.csgraph import connected_components, shortest_path

from follow_up_checks import DEGREE_LABELS, SEEDS as REWIRE_SEEDS, WINDOW, degree_bin
from structural_analysis import MODEL_REPLICATES, SEED, load_graphs, sampled_mean_path_length


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "theory"
MIN_TAIL = 50
UNCERTAINTY_DRAWS = 200
FIT_TEST_DRAWS = 500
REMOVAL_REPLICATES = 20
RANDOM_FRACTIONS = np.r_[np.arange(0, 0.8, 0.05), np.arange(0.8, 0.98, 0.01), 0.98, 0.985, 0.99, 0.995]
TARGETED_FRACTIONS = np.r_[0, 0.001, 0.005, 0.01, 0.02, 0.03, 0.05, 0.075, np.arange(0.1, 0.95, 0.025)]
COLLAPSE_SHARE = 0.01
COLORS = {"Observed": "#D99A36", "Rewired": "#287D8E", "BA": "#9B7DB8", "ER": "#728393"}


# ---------------------------------------------------------------- reference graphs
def reference_graphs(projection):
    """Rebuild the ER, BA, and rewired graphs with the seeds used by the earlier scripts."""
    n, links = projection.number_of_nodes(), projection.number_of_edges()
    ba_links = round(links / n)
    er = [nx.gnm_random_graph(n, links, seed=SEED + i) for i in range(MODEL_REPLICATES)]
    ba = [nx.barabasi_albert_graph(n, ba_links, seed=SEED + i) for i in range(MODEL_REPLICATES)]
    swaps = 10 * links
    rewired = []
    for seed in REWIRE_SEEDS:
        graph = projection.copy()
        nx.double_edge_swap(graph, nswap=swaps, max_tries=20 * swaps, seed=seed)
        rewired.append(graph)
    return er, ba, rewired


def graph_row(graph, label, family, seed):
    degrees = np.array([degree for _, degree in graph.degree()], dtype=float)
    local = nx.clustering(graph)
    with_triples = [local[node] for node, degree in graph.degree() if degree >= 2]
    largest = graph.subgraph(max(nx.connected_components(graph), key=len))
    communities = nx.community.louvain_communities(graph, seed=seed)
    return {
        "network": label, "family": family,
        "louvain_modularity": nx.community.modularity(graph, communities),
        "mean_degree": degrees.mean(), "degree_std": degrees.std(),
        "max_degree": degrees.max(),
        "heterogeneity_kappa": (degrees ** 2).mean() / degrees.mean(),
        "transitivity": nx.transitivity(graph),
        "average_clustering_all_nodes": float(np.mean(list(local.values()))),
        "average_clustering_degree_2_plus": float(np.mean(with_triples)),
        "degree_assortativity": nx.degree_assortativity_coefficient(graph),
        "largest_component_share": len(largest) / len(graph),
        "sampled_mean_path_lcc": sampled_mean_path_length(largest, seed=seed),
    }


def exact_path_statistics(graph):
    """Exact mean distance and diameter on the largest connected component."""
    largest = graph.subgraph(max(nx.connected_components(graph), key=len))
    matrix = nx.to_scipy_sparse_array(largest, format="csr", weight=None)
    n = matrix.shape[0]
    total, diameter = 0.0, 0
    for start in range(0, n, 256):
        distances = shortest_path(matrix, method="D", directed=False, unweighted=True,
                                  indices=np.arange(start, min(start + 256, n)))
        total += distances.sum()
        diameter = max(diameter, int(distances.max()))
    return total / (n * (n - 1)), diameter


# ---------------------------------------------------------------- formula predictions
def model_expectations(rows, exact_mean_path, tails, n, links, ba_links, growth):
    """Set formula values beside simulated and observed values for each quantity."""
    table = pd.DataFrame(rows)
    c = 2 * links / n
    p = 2 * links / (n * (n - 1))
    # Week 3: the giant component fraction solves S = 1 - exp(-cS) when c > 1.
    giant = optimize.brentq(lambda s: s - 1 + np.exp(-c * s), 1e-6, 1)
    log_n = np.log(n)

    def stat(family, column):
        values = table.loc[table.family == family, column]
        return values.mean(), values.std()

    observed_tail = tails.set_index("measure")
    spec = [
        ("Mean degree", "mean_degree", "<k> = 2L/N; BA tends to 2m", c, 2 * ba_links),
        ("Degree standard deviation", "degree_std", "ER: sqrt(<k>) (Poisson)", np.sqrt(c), np.nan),
        ("Maximum degree", "max_degree", "ER: N P(K >= k_max) = 1; BA: m sqrt(N)",
         stats.poisson.isf(1 / n, c), ba_links * np.sqrt(n)),
        ("Heterogeneity <k^2>/<k>", "heterogeneity_kappa", "ER: <k> + 1", c + 1, np.nan),
        ("Largest component share", "largest_component_share", "ER: S = 1 - exp(-<k>S); BA: connected", giant, 1.0),
        ("Mean path length (largest component)", "sampled_mean_path_lcc",
         "ER: ln N / ln <k>; BA: ln N / ln ln N", log_n / np.log(c), log_n / np.log(log_n)),
        ("Average local clustering", "average_clustering_all_nodes",
         "ER: p = <k>/(N-1); BA scales as (ln N)^2 / N", p, log_n ** 2 / n),
        ("Transitivity", "transitivity", "ER: p", p, np.nan),
        ("Degree assortativity", "degree_assortativity", "ER: 0", 0.0, np.nan),
        ("Louvain modularity", "louvain_modularity", "No simple formula; simulated only", np.nan, np.nan),
    ]
    output = []
    for name, column, formula, er_formula, ba_formula in spec:
        observed = table.loc[table.family == "Observed", column].iloc[0]
        if column == "sampled_mean_path_lcc":
            observed = exact_mean_path
        output.append({
            "quantity": name, "formula": formula, "observed": observed,
            "er_formula": er_formula, "er_simulated_mean": stat("ER", column)[0], "er_simulated_std": stat("ER", column)[1],
            "ba_formula": ba_formula, "ba_simulated_mean": stat("BA", column)[0], "ba_simulated_std": stat("BA", column)[1],
            "rewired_mean": stat("Rewired", column)[0], "rewired_std": stat("Rewired", column)[1],
            "internal_link_formula": np.nan,
            "internal_link_simulated_mean": stat("Internal-link", column)[0],
            "internal_link_simulated_std": stat("Internal-link", column)[1],
        })
    output.append({
        "quantity": "Degree tail exponent gamma", "formula": "BA: 3; internal links: 2 + m/(m + 2n); ER: no power-law tail",
        "observed": observed_tail.loc["Undirected degree", "gamma"],
        "er_formula": np.nan, "er_simulated_mean": np.nan, "er_simulated_std": np.nan,
        "ba_formula": 3.0, "ba_simulated_mean": observed_tail.loc["BA reference", "gamma"],
        "ba_simulated_std": observed_tail.loc["BA reference", "gamma_bootstrap_std"],
        "rewired_mean": np.nan, "rewired_std": np.nan,
        "internal_link_formula": growth["gamma_double_preferential_attachment"],
        "internal_link_simulated_mean": observed_tail.loc["Internal-link reference", "gamma"],
        "internal_link_simulated_std": observed_tail.loc["Internal-link reference", "gamma_bootstrap_std"],
    })
    return pd.DataFrame(output)


# ---------------------------------------------------------------- degree tails
def fit_power_tail(sample, min_tail=MIN_TAIL):
    """Choose k_min by the smallest KS distance; estimate gamma by discrete maximum likelihood."""
    values, counts = np.unique(sample, return_counts=True)
    remaining = counts[::-1].cumsum()[::-1]
    best = None
    for start, k_min in enumerate(values):
        n_tail = remaining[start]
        if n_tail < min_tail:
            break
        tail_values, tail_counts = values[start:].astype(float), counts[start:]
        log_total = float(tail_counts @ np.log(tail_values))
        gamma = float(optimize.minimize_scalar(
            lambda g: n_tail * np.log(special.zeta(g, k_min)) + g * log_total,
            bounds=(1.05, 8.0), method="bounded", options={"xatol": 1e-4}).x)
        model_cdf = 1 - special.zeta(gamma, tail_values + 1) / special.zeta(gamma, k_min)
        distance = float(np.abs(tail_counts.cumsum() / n_tail - model_cdf).max())
        if best is None or distance < best["ks"]:
            best = {"k_min": int(k_min), "gamma": gamma, "ks": distance, "n_tail": int(n_tail)}
    return best


def discrete_power_draws(uniform, k_min, gamma):
    """Exact draws from P(k) = k^-gamma / zeta(gamma, k_min) for k >= k_min.

    Each draw is the largest k whose tail probability zeta(gamma, k) / zeta(gamma, k_min)
    is at least 1 - u, found by doubling and then bisection (Clauset et al. 2009, App. D).
    """
    target = 1 - uniform
    norm = special.zeta(gamma, k_min)
    low = np.full(len(target), float(k_min))
    high = low.copy()
    while True:
        above = special.zeta(gamma, high) / norm >= target
        if not above.any():
            break
        low[above] = high[above]
        high[above] *= 2
    while (high - low > 1).any():
        middle = np.floor((low + high) / 2)
        above = special.zeta(gamma, middle) / norm >= target
        low = np.where(above, middle, low)
        high = np.where(above, high, middle)
    return low


def synthetic_sample(rng, sample, fit):
    """Keep the observed body below k_min and draw the tail exactly from the fitted discrete power law."""
    body = sample[sample < fit["k_min"]]
    n_tail = rng.binomial(len(sample), fit["n_tail"] / len(sample))
    tail = discrete_power_draws(rng.random(n_tail), fit["k_min"], fit["gamma"])
    resampled = rng.choice(body, len(sample) - n_tail) if len(body) else np.empty(0)
    return np.concatenate([resampled, tail])


def power_pointwise(tail, k_min, gamma):
    return -gamma * np.log(tail) - np.log(special.zeta(gamma, k_min))


def fit_lognormal(tail, k_min):
    """Discretized lognormal conditioned on k >= k_min."""
    def pointwise(mu, sigma):
        low = stats.norm.sf((np.log(tail - 0.5) - mu) / sigma)
        high = stats.norm.sf((np.log(tail + 0.5) - mu) / sigma)
        norm = stats.norm.sf((np.log(k_min - 0.5) - mu) / sigma)
        return np.log(np.clip(low - high, 1e-300, None)) - np.log(max(norm, 1e-300))

    def negative(params):
        mu, sigma = params
        return np.inf if sigma < 0.01 or mu < -30 else -pointwise(mu, sigma).sum()

    logs = np.log(tail)
    result = optimize.minimize(negative, [logs.mean(), max(logs.std(), 0.1)], method="Nelder-Mead",
                               options={"xatol": 1e-3, "fatol": 1e-3, "maxiter": 2000})
    return pointwise(*result.x), result.x


def fit_exponential(tail, k_min):
    """Geometric tail, the thin-tailed baseline."""
    p = 1 / (1 + (tail - k_min).mean())
    return np.log(p) + (tail - k_min) * np.log(1 - p)


def fit_truncated(tail, k_min):
    """Power law with an exponential cutoff, normalized by a numerical sum."""
    support = np.arange(k_min, 100_000, dtype=float)
    log_support = np.log(support)

    def pointwise(gamma, rate):
        return -gamma * np.log(tail) - rate * tail - np.log(np.exp(-gamma * log_support - rate * support).sum())

    def negative(params):
        return np.inf if params[1] < 0 or params[0] < 0 else -pointwise(*params).sum()

    result = optimize.minimize(negative, [2.0, 1e-3], method="Nelder-Mead",
                               options={"xatol": 1e-5, "fatol": 1e-3, "maxiter": 2000})
    return pointwise(*result.x), result.x


def vuong(first, second):
    """Log-likelihood ratio and two-sided p value; a positive ratio favors the first model."""
    difference = first - second
    ratio = difference.sum()
    spread = difference.std()
    z = ratio / (np.sqrt(len(difference)) * spread) if spread else 0.0
    return float(ratio), float(special.erfc(abs(z) / np.sqrt(2)))


def tail_row(measure, sample, rng):
    sample = sample[sample >= 1].astype(float)
    fit = fit_power_tail(sample)
    resampled = [fit_power_tail(rng.choice(sample, len(sample))) for _ in range(UNCERTAINTY_DRAWS)]
    gammas = np.array([item["gamma"] for item in resampled])
    cutoffs = np.array([item["k_min"] for item in resampled])
    distances = [fit_power_tail(synthetic_sample(rng, sample, fit))["ks"] for _ in range(FIT_TEST_DRAWS)]
    tail = sample[sample >= fit["k_min"]]
    power = power_pointwise(tail, fit["k_min"], fit["gamma"])
    lognormal, lognormal_params = fit_lognormal(tail, fit["k_min"])
    truncated, truncated_params = fit_truncated(tail, fit["k_min"])
    lr_log, p_log = vuong(power, lognormal)
    lr_exp, p_exp = vuong(power, fit_exponential(tail, fit["k_min"]))
    lr_cut = float((power - truncated).sum())
    return {
        "measure": measure, "nodes_with_positive_degree": len(sample),
        "k_min": fit["k_min"], "tail_nodes": fit["n_tail"], "tail_share": fit["n_tail"] / len(sample),
        "gamma": fit["gamma"], "gamma_bootstrap_std": gammas.std(ddof=1),
        "gamma_ci_low": np.quantile(gammas, 0.025), "gamma_ci_high": np.quantile(gammas, 0.975),
        "k_min_ci_low": np.quantile(cutoffs, 0.025), "k_min_ci_high": np.quantile(cutoffs, 0.975),
        "ks_distance": fit["ks"], "goodness_of_fit_p": float(np.mean(np.array(distances) >= fit["ks"])),
        "lr_vs_lognormal": lr_log, "p_vs_lognormal": p_log,
        "lr_vs_exponential": lr_exp, "p_vs_exponential": p_exp,
        "lr_vs_truncated": lr_cut, "p_vs_truncated": float(stats.chi2.sf(max(-2 * lr_cut, 0), 1)),
        "truncated_gamma": truncated_params[0], "truncated_rate": truncated_params[1],
        "lognormal_mu": lognormal_params[0], "lognormal_sigma": lognormal_params[1],
        "expected_max_degree": fit["k_min"] * fit["n_tail"] ** (1 / (fit["gamma"] - 1)),
        "observed_max_degree": sample.max(),
    }


def degree_tails(directed, projection, ba_graphs, internal_graphs, rng):
    nodes = list(projection)
    rows = [
        tail_row("Undirected degree", np.array([projection.degree(v) for v in nodes]), rng),
        tail_row("Positive in-degree", np.array([directed.in_degree(v) for v in nodes]), rng),
        tail_row("Positive out-degree", np.array([directed.out_degree(v) for v in nodes]), rng),
    ]
    # The same estimator on simulated graphs shows what it recovers when the true
    # exponent is known. For these rows the spread is across realizations.
    for measure, graphs in (("BA reference", ba_graphs), ("Internal-link reference", internal_graphs)):
        fits = [fit_power_tail(np.array([d for _, d in graph.degree()], dtype=float)) for graph in graphs]
        gammas = [item["gamma"] for item in fits]
        rows.append({"measure": measure, "nodes_with_positive_degree": graphs[0].number_of_nodes(),
                     "k_min": float(np.median([item["k_min"] for item in fits])),
                     "gamma": float(np.mean(gammas)), "gamma_bootstrap_std": float(np.std(gammas, ddof=1)),
                     "gamma_ci_low": float(np.min(gammas)), "gamma_ci_high": float(np.max(gammas))})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- attachment
DESIGNS = (
    ("Uniform", False, None, False, 1),
    ("Tenure and activity", True, "both", False, 5),
    ("Tenure only", True, None, False, 5),
    ("Activity only", False, "both", False, 5),
    ("Tenure and ratings given", True, "given", False, 5),
    ("Uniform, first rating in a pair", False, None, True, 1),
    ("Tenure and activity, first rating in a pair", True, "both", True, 5),
)


def attachment_exponent(rows, target_degrees, shape):
    """Maximum likelihood for choice probability proportional to (k + 1) ** alpha."""
    columns = np.concatenate([item[0] for item in rows])
    data = np.concatenate([item[1] for item in rows]).astype(float)
    indptr = np.r_[0, np.cumsum([len(item[0]) for item in rows])]
    matrix = sparse.csr_matrix((data, columns, indptr), shape=(len(rows), shape))
    x = np.log(np.arange(shape) + 1.0)
    chosen = x[np.asarray(target_degrees)].sum()

    def negative(alpha):
        return np.log(matrix @ np.exp(alpha * x)).sum() - alpha * chosen

    alpha = float(optimize.minimize_scalar(negative, bounds=(-2, 4), method="bounded", options={"xatol": 1e-4}).x)
    weights = np.exp(alpha * x)
    total = matrix @ weights
    mean = (matrix @ (weights * x)) / total
    second = (matrix @ (weights * x * x)) / total
    return alpha, float(1 / np.sqrt((second - mean ** 2).sum()))


def attachment_benchmarks(positive):
    """Recompute recipient-choice benchmarks and estimate an attachment exponent for each."""
    ids = pd.Index(sorted(set(positive.source) | set(positive.target)))
    lookup = {node: i for i, node in enumerate(ids)}
    n = len(ids)
    in_degree_limit = int(positive.groupby("target").size().max()) + 2
    bin_of = np.array([degree_bin(k) for k in range(in_degree_limit)])
    active = np.zeros(n, dtype=bool)
    first_seen = np.zeros(n)
    indegree = np.zeros(n, dtype=int)
    given = np.zeros(n, dtype=int)
    received = np.zeros(n, dtype=int)
    rated = [[] for _ in range(n)]
    rated_by = [[] for _ in range(n)]
    pair_time = {}
    history = deque()
    results = {design[0]: {"observed": np.zeros(7), "expected": np.zeros(7), "expected_k": np.zeros(7),
                           "rows": [], "targets": []} for design in DESIGNS}
    returned = np.zeros(7)
    eligible_by_bin = np.zeros(7)
    lags = []
    eligible = 0
    for source, target, time in positive[["source", "target", "time"]].itertuples(index=False, name=None):
        u, v = lookup[source], lookup[target]
        while history and history[0][0] < time - WINDOW:
            _, old_u, old_v = history.popleft()
            given[old_u] -= 1
            received[old_v] -= 1
        reply = (target, source) in pair_time
        if active[v]:
            eligible += 1
            degree_group = bin_of[indegree[v]]
            eligible_by_bin[degree_group] += 1
            if reply:
                returned[degree_group] += 1
                lags.append((time - pair_time[(target, source)]) / 86400)
            base = active.copy()
            base[u] = False
            if rated[u]:
                base[rated[u]] = False
            tenure = np.digitize((time - first_seen) / 86400, [90, 365])
            both = np.digitize(given + received, [1, 3, 10])
            only_given = np.digitize(given, [1, 3, 10])
            for name, use_tenure, activity, first_only, minimum in DESIGNS:
                if first_only and reply:
                    continue
                mask = base
                if first_only and rated_by[u]:
                    mask = mask.copy()
                    mask[rated_by[u]] = False
                if use_tenure:
                    mask = mask & (tenure == tenure[v])
                if activity == "both":
                    mask = mask & (both == both[v])
                elif activity == "given":
                    mask = mask & (only_given == only_given[v])
                size = int(mask.sum())
                if size < minimum or not mask[v]:
                    continue
                histogram = np.bincount(indegree[mask])
                degrees = np.flatnonzero(histogram)
                counts = histogram[degrees]
                record = results[name]
                groups = bin_of[degrees]
                record["observed"][degree_group] += 1
                record["expected"] += np.bincount(groups, weights=counts / size, minlength=7)
                record["expected_k"] += np.bincount(groups, weights=counts * degrees / size, minlength=7)
                record["rows"].append((degrees.astype(np.int32), counts.astype(np.int32)))
                record["targets"].append(indegree[v])
        for node in (u, v):
            if not active[node]:
                active[node] = True
                first_seen[node] = time
        indegree[v] += 1
        given[u] += 1
        received[v] += 1
        rated[u].append(v)
        rated_by[v].append(u)
        pair_time[(source, target)] = time
        history.append((time, u, v))

    rows, kernels = [], []
    for name, *_ in DESIGNS:
        record = results[name]
        ratio = record["observed"] / record["expected"]
        alpha, error = attachment_exponent(record["rows"], record["targets"], in_degree_limit)
        row = {"benchmark": name, "events": int(record["observed"].sum()),
               "share_of_eligible_events": record["observed"].sum() / eligible,
               "attachment_exponent_alpha": alpha, "alpha_standard_error": error}
        row.update({f"ratio_{label}": value for label, value in zip(DEGREE_LABELS, ratio)})
        rows.append(row)
        kernels.extend({"benchmark": name, "prior_positive_in_degree": label,
                        "mean_prior_degree": k / e, "observed_over_expected": r}
                       for label, k, e, r in zip(DEGREE_LABELS, record["expected_k"], record["expected"], ratio))
    reciprocation = pd.DataFrame({
        "prior_positive_in_degree": DEGREE_LABELS, "eligible_events": eligible_by_bin.astype(int),
        "events_returning_an_earlier_rating": returned.astype(int),
        "share_returning": returned / eligible_by_bin})
    summary = {"eligible_events": eligible, "events_returning_an_earlier_rating": int(returned.sum()),
               "share_returning": float(returned.sum() / eligible),
               "median_days_to_return": float(np.median(lags)),
               "share_returned_within_7_days": float(np.mean(np.array(lags) <= 7))}
    return pd.DataFrame(rows), pd.DataFrame(kernels), reciprocation, summary


# ---------------------------------------------------------------- growth
def growth_by_link_type(positive):
    """Count undirected links that arrive with a new user and links between existing users.

    BA assumes every link arrives with a new node. Each new link is classified at the
    moment its undirected pair first appears, to give the growth rates m and n used by
    the double preferential attachment formula gamma = 2 + m / (m + 2n)
    (Barabasi, Network Science, Section 6.5, Eq. 6.27).
    """
    seen, links = set(), set()
    with_new_user = internal = 0
    for source, target in positive[["source", "target"]].itertuples(index=False, name=None):
        pair = (min(source, target), max(source, target))
        if pair not in links:
            links.add(pair)
            if source in seen and target in seen:
                internal += 1
            else:
                with_new_user += 1
        seen.update(pair)
    m, n = with_new_user / len(seen), internal / len(seen)
    return {
        "users_in_positive_ratings": len(seen), "undirected_links": len(links),
        "links_arriving_with_a_new_user": with_new_user, "links_between_existing_users": internal,
        "share_between_existing_users": internal / len(links),
        "links_per_new_user_m": m, "internal_links_per_new_user_n": n,
        "gamma_double_preferential_attachment": 2 + m / (m + 2 * n),
    }


def internal_link_graphs(growth, rng):
    """Simulate growth where existing users also link, with both ends chosen by degree.

    Each new user brings one preferential link (m is close to 1 here) and each step adds
    n internal links on average. This is the double preferential attachment model in
    Barabasi, Network Science, Section 6.5, whose degree exponent is
    gamma = 2 + m / (m + 2n) (Eq. 6.27).
    """
    graphs = []
    for _ in range(MODEL_REPLICATES):
        graph = nx.Graph([(0, 1)])
        ends = [0, 1]
        for node in range(2, growth["users_in_positive_ratings"]):
            target = ends[rng.integers(len(ends))]
            graph.add_edge(node, target)
            ends += [node, target]
            for _ in range(rng.poisson(growth["internal_links_per_new_user_n"])):
                # Retry so a repeated pair does not silently lower the link count.
                for _ in range(50):
                    first, second = ends[rng.integers(len(ends))], ends[rng.integers(len(ends))]
                    if first != second and not graph.has_edge(first, second):
                        graph.add_edge(first, second)
                        ends += [first, second]
                        break
        graphs.append(graph)
    return graphs


# ---------------------------------------------------------------- percolation
def component_statistics(matrix, keep, original_n):
    _, labels = connected_components(matrix[keep][:, keep], directed=False)
    sizes = np.bincount(labels).astype(float)
    largest = sizes.max()
    rest = sizes.sum() - largest
    finite = ((sizes ** 2).sum() - largest ** 2) / rest if rest else 0.0
    return largest / original_n, finite


def percolation(graphs, rng):
    """Remove nodes at random and by original degree across a wide range of fractions."""
    curves, thresholds = [], []
    for label, graph in graphs.items():
        nodes = sorted(graph)
        matrix = nx.to_scipy_sparse_array(graph, nodelist=nodes, format="csr", weight=None)
        n = len(nodes)
        degrees = np.asarray(matrix.sum(axis=1)).ravel()
        for fraction in RANDOM_FRACTIONS:
            removed = round(fraction * n)
            draws = []
            for _ in range(REMOVAL_REPLICATES):
                keep = np.ones(n, dtype=bool)
                keep[rng.choice(n, removed, replace=False)] = False
                draws.append(component_statistics(matrix, keep, n))
            draws = np.array(draws)
            curves.append({"network": label, "strategy": "random", "fraction_removed": fraction,
                           "largest_component_share": draws[:, 0].mean(),
                           "largest_component_std": draws[:, 0].std(ddof=1),
                           "mean_finite_cluster_size": draws[:, 1].mean()})
        order = np.lexsort((np.arange(n), -degrees))
        for fraction in TARGETED_FRACTIONS:
            keep = np.ones(n, dtype=bool)
            keep[order[:round(fraction * n)]] = False
            share, finite = component_statistics(matrix, keep, n)
            curves.append({"network": label, "strategy": "highest_degree_first", "fraction_removed": fraction,
                           "largest_component_share": share, "largest_component_std": 0.0,
                           "mean_finite_cluster_size": finite})
        kappa = (degrees ** 2).sum() / degrees.sum()
        frame = pd.DataFrame([row for row in curves if row["network"] == label])
        collapse = {}
        for strategy in ("random", "highest_degree_first"):
            part = frame[(frame.strategy == strategy) & (frame.largest_component_share < COLLAPSE_SHARE)]
            collapse[strategy] = float(part.fraction_removed.min()) if len(part) else np.nan
        thresholds.append({
            "network": label, "heterogeneity_kappa": kappa,
            "molloy_reed_threshold": 1 - 1 / (kappa - 1),
            "random_removal_collapse_fraction": collapse["random"],
            "targeted_removal_collapse_fraction": collapse["highest_degree_first"],
        })
    return pd.DataFrame(curves), pd.DataFrame(thresholds)


# ---------------------------------------------------------------- centrality
def centrality_check(directed):
    stored = pd.read_csv(ROOT / "outputs/structure/directed_centrality.csv")
    exact = nx.betweenness_centrality(directed, normalized=True)
    stored["betweenness_exact"] = stored.node.map(exact)
    connected = stored[(stored.positive_in_degree + stored.positive_out_degree) > 0]
    top = {size: set(stored.nlargest(size, "betweenness_exact").node) for size in (10, 20)}
    summary = {
        "spearman_sampled_vs_exact_betweenness": float(stats.spearmanr(connected.betweenness_approx, connected.betweenness_exact).statistic),
        "spearman_in_degree_vs_out_degree": float(stats.spearmanr(connected.positive_in_degree, connected.positive_out_degree).statistic),
        "spearman_in_degree_vs_exact_betweenness": float(stats.spearmanr(connected.positive_in_degree, connected.betweenness_exact).statistic),
        "top_10_overlap_sampled_vs_exact": len(top[10] & set(stored.nlargest(10, "betweenness_approx").node)),
        "top_20_overlap_sampled_vs_exact": len(top[20] & set(stored.nlargest(20, "betweenness_approx").node)),
        "top_10_overlap_in_degree_vs_exact": len(top[10] & set(stored.nlargest(10, "positive_in_degree").node)),
    }
    table = stored.sort_values(["betweenness_exact", "node"], ascending=[False, True]).head(20).copy()
    table.insert(0, "betweenness_rank", range(1, 21))
    ranks = stored.positive_in_degree.rank(ascending=False, method="min")
    table["in_degree_rank"] = ranks[table.index].astype(int)
    return table, summary


# ---------------------------------------------------------------- figures
def figure_tails(tails, directed, projection):
    plt.style.use("seaborn-v0_8-whitegrid")
    nodes = list(projection)
    samples = {
        "Undirected degree": np.array([projection.degree(v) for v in nodes]),
        "Positive in-degree": np.array([directed.in_degree(v) for v in nodes]),
        "Positive out-degree": np.array([directed.out_degree(v) for v in nodes]),
    }
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.9), sharey=True)
    handles = None
    for ax, (measure, sample) in zip(axes, samples.items()):
        sample = sample[sample >= 1]
        row = tails.set_index("measure").loc[measure]
        values, counts = np.unique(sample, return_counts=True)
        ccdf = counts[::-1].cumsum()[::-1] / counts.sum()
        grid = np.unique(np.logspace(np.log10(row.k_min), np.log10(values.max()), 80).astype(int))
        share = row.tail_nodes / len(sample)
        power = share * special.zeta(row.gamma, grid) / special.zeta(row.gamma, row.k_min)
        lognormal = share * (stats.norm.sf((np.log(grid - 0.5) - row.lognormal_mu) / row.lognormal_sigma)
                             / stats.norm.sf((np.log(row.k_min - 0.5) - row.lognormal_mu) / row.lognormal_sigma))
        reference = share * (grid / row.k_min) ** -2.0
        a, = ax.loglog(values, ccdf, marker="o", markersize=3, linestyle="none", color="#728393", label="Observed CCDF")
        b, = ax.loglog(grid, power, color="#D99A36", linewidth=2, label="Fitted power-law tail")
        c, = ax.loglog(grid, lognormal, color="#287D8E", linewidth=2, label="Fitted lognormal tail")
        d, = ax.loglog(grid, reference, color="#132B3F", linewidth=1, linestyle="--", label="BA slope (gamma = 3)")
        handles = [a, b, c, d]
        ax.set_title(f"{measure}: gamma = {row.gamma:.2f}, k_min = {int(row.k_min)}", fontsize=10)
        ax.set_xlabel("Degree k")
        ax.set_ylim(1 / (2 * len(sample)), 1.2)
    axes[0].set_ylabel("Share of nodes with degree at least k")
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=9, frameon=False)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(OUT / "degree_ccdf_fits.png", dpi=200)
    plt.close(fig)


def figure_kernel(kernels, benchmarks):
    plt.style.use("seaborn-v0_8-whitegrid")
    shown = (("Uniform", "#D99A36", "o"), ("Tenure and ratings given", "#9B7DB8", "^"),
             ("Tenure and activity", "#287D8E", "s"))
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    alphas = benchmarks.set_index("benchmark").attachment_exponent_alpha
    for name, color, marker in shown:
        part = kernels[(kernels.benchmark == name) & (kernels.mean_prior_degree > 0.5)]
        ax.loglog(part.mean_prior_degree + 1, part.observed_over_expected, marker=marker, markersize=6,
                  linewidth=2, color=color, label=f"{name} (alpha = {alphas[name]:.2f})")
    grid = np.array([2.0, 200.0])
    ax.loglog(grid, grid / grid[0] * 0.25, color="#132B3F", linestyle="--", linewidth=1, label="Slope 1: linear attachment (BA)")
    ax.axhline(1, color="#728393", linewidth=1)
    ax.set(xlabel="Prior positive in-degree + 1 (mean within each degree group)",
           ylabel="Observed / expected recipients", title="Attachment depends on the benchmark")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "attachment_kernel.png", dpi=200)
    plt.close(fig)


def figure_percolation(curves, thresholds):
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4), sharey=True)
    for label, color in COLORS.items():
        for ax, strategy in zip(axes, ("random", "highest_degree_first")):
            part = curves[(curves.network == label) & (curves.strategy == strategy)]
            ax.plot(part.fraction_removed, part.largest_component_share, color=color, linewidth=2, label=label)
    limits = thresholds.set_index("network").molloy_reed_threshold
    axes[0].axvline(limits["Observed"], color=COLORS["Observed"], linestyle=":", linewidth=1.5,
                    label=f"Molloy-Reed, observed ({limits['Observed']:.3f})")
    axes[0].axvline(limits["ER"], color=COLORS["ER"], linestyle=":", linewidth=1.5,
                    label=f"Molloy-Reed, ER ({limits['ER']:.3f})")
    axes[0].set(title="Random removal", xlabel="Fraction of users removed", ylabel="Largest component / original users")
    axes[1].set(title="Highest original degree removed first", xlabel="Fraction of users removed", xlim=(0, 0.7))
    axes[0].legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    fig.savefig(OUT / "percolation_vs_theory.png", dpi=200)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    ratings, directed, projection = load_graphs()
    positive = ratings[ratings.rating > 0]
    er, ba, rewired = reference_graphs(projection)
    growth = growth_by_link_type(positive)
    internal = internal_link_graphs(growth, rng)

    # Confirm these are the same graphs the earlier scripts measured.
    stored = pd.read_csv(ROOT / "outputs/structure/network_metrics.csv").set_index("network")
    stored_rewires = pd.read_csv(ROOT / "outputs/follow_up/degree_preserving_null.csv")
    assert abs(nx.transitivity(er[0]) - stored.loc["ER_01", "transitivity"]) < 1e-12
    assert abs(nx.transitivity(ba[0]) - stored.loc["BA_01", "transitivity"]) < 1e-12
    assert abs(nx.transitivity(rewired[0]) - stored_rewires.loc[stored_rewires.seed == REWIRE_SEEDS[0], "transitivity"].iloc[0]) < 1e-12

    rows = [graph_row(projection, "observed", "Observed", SEED)]
    rows += [graph_row(graph, f"ER_{i + 1:02d}", "ER", SEED + i) for i, graph in enumerate(er)]
    rows += [graph_row(graph, f"BA_{i + 1:02d}", "BA", SEED + i) for i, graph in enumerate(ba)]
    rows += [graph_row(graph, f"rewire_{seed}", "Rewired", seed) for seed, graph in zip(REWIRE_SEEDS, rewired)]
    rows += [graph_row(graph, f"internal_{i + 1:02d}", "Internal-link", SEED + i) for i, graph in enumerate(internal)]
    reference = pd.DataFrame(rows)

    exact_mean, exact_diameter = exact_path_statistics(projection)
    assert exact_diameter == 14
    tails = degree_tails(directed, projection, ba, internal, rng)
    n, links = projection.number_of_nodes(), projection.number_of_edges()
    expectations = model_expectations(rows, exact_mean, tails, n, links, round(links / n), growth)

    benchmarks, kernels, reciprocation, reply_summary = attachment_benchmarks(positive)
    # The two established benchmarks must reproduce the stored results exactly.
    table = benchmarks.set_index("benchmark")
    uniform = pd.read_csv(ROOT / "outputs/temporal/target_choice_by_prior_degree.csv").set_index("prior_positive_in_degree")
    matched = pd.read_csv(ROOT / "outputs/follow_up/matched_target_choice.csv").set_index("prior_positive_in_degree")
    for label in DEGREE_LABELS:
        assert abs(table.loc["Uniform", f"ratio_{label}"] - uniform.loc[label, "observed_over_expected"]) < 1e-9
        assert abs(table.loc["Tenure and activity", f"ratio_{label}"] - matched.loc[label, "observed_over_expected"]) < 1e-9

    curves, thresholds = percolation(
        {"Observed": projection, "Rewired": rewired[0], "BA": ba[0], "ER": er[0]}, rng)
    centrality, centrality_summary = centrality_check(directed)

    observed = reference[reference.family == "Observed"].iloc[0]
    er_rows = reference[reference.family == "ER"]
    rewired_rows = reference[reference.family == "Rewired"]
    small_world = {
        "clustering_ratio_to_er": float(observed.average_clustering_all_nodes / er_rows.average_clustering_all_nodes.mean()),
        "path_ratio_to_er": float(exact_mean / er_rows.sampled_mean_path_lcc.mean()),
        "clustering_ratio_to_rewired": float(observed.average_clustering_all_nodes / rewired_rows.average_clustering_all_nodes.mean()),
        "path_ratio_to_rewired": float(exact_mean / rewired_rows.sampled_mean_path_lcc.mean()),
    }
    small_world["small_world_sigma_vs_er"] = small_world["clustering_ratio_to_er"] / small_world["path_ratio_to_er"]
    small_world["small_world_sigma_vs_rewired"] = small_world["clustering_ratio_to_rewired"] / small_world["path_ratio_to_rewired"]

    reference.to_csv(OUT / "reference_metrics.csv", index=False)
    expectations.to_csv(OUT / "model_expectations.csv", index=False)
    tails.to_csv(OUT / "degree_tail_fits.csv", index=False)
    benchmarks.to_csv(OUT / "attachment_benchmarks.csv", index=False)
    reciprocation.to_csv(OUT / "reciprocation_by_prior_degree.csv", index=False)
    curves.to_csv(OUT / "percolation_curves.csv", index=False)
    thresholds.to_csv(OUT / "percolation_thresholds.csv", index=False)
    centrality.to_csv(OUT / "centrality_comparison.csv", index=False)
    metadata = {
        "seed": SEED,
        "exact_mean_path_largest_component": exact_mean,
        "exact_diameter_largest_component": exact_diameter,
        "sampled_mean_path_stored": float(stored.loc["observed", "sampled_mean_path_lcc"]),
        "small_world": small_world,
        "centrality": centrality_summary,
        "return_ratings": reply_summary,
        "tail_method": "Discrete power-law maximum likelihood; k_min by smallest KS distance with at least "
                       f"{MIN_TAIL} tail nodes; {UNCERTAINTY_DRAWS} bootstrap draws; semi-parametric goodness of fit "
                       f"with {FIT_TEST_DRAWS} draws, tails drawn exactly from the discrete power law; Vuong tests against lognormal and exponential, nested test against a cutoff",
        "attachment_method": "Conditional logit: choice probability proportional to (k + 1) ** alpha among each event's "
                             "candidates. Standard errors treat events as independent, so they are optimistic.",
        "percolation_method": f"{REMOVAL_REPLICATES} random replicates per fraction on one realization of each graph; "
                              f"collapse is the first tested fraction leaving a largest component under {COLLAPSE_SHARE:.0%} of original users",
        "growth": growth,
        "limits": "Formula values are large-network approximations. Comparisons are descriptive and do not identify a mechanism.",
    }
    (OUT / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")

    figure_tails(tails, directed, projection)
    figure_kernel(kernels, benchmarks)
    figure_percolation(curves, thresholds)
    print(expectations.round(4).to_string(index=False))
    print(tails.round(4).T.to_string())
    print(benchmarks.round(3).to_string(index=False))
    print(reciprocation.round(3).to_string(index=False))
    print(thresholds.round(4).to_string(index=False))
    print(centrality.round(4).to_string(index=False))
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
