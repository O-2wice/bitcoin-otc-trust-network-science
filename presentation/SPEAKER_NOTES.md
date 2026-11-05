# Presentation reading notes

Read the spoken paragraphs. Timing and source lines are preparation notes. The PowerPoint contains the same script in 18-point text.

## 1. The Bitcoin OTC Trust Network

**Timing:** 20 seconds

We study how Bitcoin OTC accounts rated one another and how positive ratings built up over time. Our network contains accounts as nodes and ratings as directed links.

The key finding is that accumulated ratings and new yearly ratings tell different stories. We will explain the network, compare it with reference models, and then examine that difference.

**Sources / preparation:** SNAP Bitcoin OTC dataset: https://snap.stanford.edu/data/soc-sign-bitcoinotc.html

## 2. Why study Bitcoin OTC ratings?

**Timing:** 40 seconds

Bitcoin OTC used a web of trust: accounts could give other accounts positive or negative ratings. The file contains 35,592 ratings among 5,881 accounts, recorded from November 2010 to January 2016.

Our question is how positive-rating concentration changed as this record grew. We also ask whether already highly rated users still stand out when we change the comparison benchmark. These are recorded opinions. They do not verify trades or prove that an account was trustworthy.

**Sources / preparation:** SNAP dataset description; Kumar et al., Edge Weight Prediction in Weighted Signed Networks, ICDM 2016.

## 3. A rating becomes a directed link

**Timing:** 55 seconds

Each node is an account. The arrow points from the rater to the recipient. In these real records, user 6 rated user 2 positive four; user 2 later rated user 6 positive five.

The directed network keeps those two positive arrows separately. The score and time remain attributes. In the undirected network, the same two accounts share one link. We use the undirected network for the model comparisons and community analysis.

The main measures count links, rather than adding rating scores. A path counts hops: one link means distance one. Negative ratings remain in the full signed graph and the Cytoscape view.

**Sources / preparation:** Source CSV records; scripts/structural_analysis.py; REPRODUCIBILITY.md.

## 4. Communities in the positive network

**Timing:** 55 seconds

This overview contains all 5,881 accounts and 18,591 undirected positive links. The largest component contains 5,551 accounts. The separate panel makes the small components and 308 isolated accounts visible.

Colours show Louvain groups. The five largest contain between 631 and 1,096 accounts. These groups also connect to one another: 44.2 percent of Group 4's link endpoints lead outside its group.

There are 33 groups with multiple accounts and 308 singleton groups. The colours describe link patterns; we have no real social labels for them. Distances on this drawing are layout choices.

**Sources / preparation:** outputs/structure/communities.csv; outputs/sensitivity/community_profiles.csv; Blondel et al. (2008), doi:10.1088/1742-5468/2008/10/P10008.

## 5. Random linking and preferential attachment

**Timing:** 50 seconds

ER keeps the observed number of accounts and links, but connects pairs at random. BA grows by adding nodes that prefer already well-connected nodes. We generated ten networks of each type.

The observed maximum degree is 788. The model averages are 17.1 for ER and 231 for BA. BA gives more uneven degrees than ER, but neither matches the observed maximum. BA has 5.15 percent fewer links because its number of new links must be a whole number.

The average degree is two L divided by N. Each undirected link has two endpoints, giving 6.32 here.

**Sources / preparation:** outputs/structure/network_metrics.csv; Erdős and Rényi (1959); Barabási and Albert (1999), doi:10.1126/science.286.5439.509.

## 6. Clustering exceeds the reference networks

**Timing:** 50 seconds

Transitivity measures how often connected triples close into triangles. It is 5.70 percent in the observed graph, compared with 0.11 percent for ER and 0.42 percent for BA.

The rewired comparison is stricter. It keeps every account's degree exactly the same, while changing its partners. Across eight rewired graphs, mean transitivity is 4.30 percent.

The observed graph therefore has more triangle closure even when degrees are fixed. These finite simulations are descriptive references. They do not tell us which social process produced the extra triangles.

**Sources / preparation:** outputs/flagship/degree_preserving_null.csv; outputs/structure/network_metrics.csv. Eight rewires, ten successful swaps per link.

## 7. CyAnimator: how ratings appeared over time

**Timing:** 45 seconds

Play the embedded clip. CyAnimator takes five year-end states and animates how their strong ratings accumulated. Teal arrows are positive and coral arrows are negative. Each arrow points from rater to recipient.

The same 22 accounts stay fixed. Five of the 76 ratings had been recorded by the end of 2011, rising to 16, 54, 73, and 76 by 2015. The fades connect annual snapshots; they do not add observations between the cutoffs.

These accounts were selected using the full record. Use the animation to illustrate link timing, and the following plots for evidence about the wider population.

**Sources / preparation:** CyAnimator 2.2.1 frame export in Cytoscape 3.10.4; outputs/cytoscape/cyanimator_provenance.json; Morris et al. (2015), doi:10.12688/f1000research.6852.2.

## 8. Concentration depends on the time window

**Timing:** 75 seconds

The blue line includes all positive ratings recorded up to each year end. The highest-rated one percent receive 15.5 percent of cumulative ratings in 2011 and 23.5 percent in 2015.

The orange line counts only ratings recorded within each year. Its top one percent share peaks at 21.0 percent in 2013, then falls to 11.3 percent in 2015. Accumulated inequality rises while concentration in new yearly ratings falls after 2013.

We reselect the top one percent separately in each view. The populations differ, and annual ratings fall from 11,138 to 929 between 2013 and 2015. These changes do not by themselves identify a cause.

**Sources / preparation:** outputs/temporal/annual_snapshots.csv; outputs/sensitivity/annual_only_concentration.csv. Both populations include users giving or receiving a positive rating, including zero-incoming users.

## 9. Triangle closure rises and reciprocity falls

**Timing:** 45 seconds

These graphs show structural evolution in the cumulative record. On the left, transitivity rises overall from 4.60 to 5.69 percent, with a dip in 2013.

On the right, reciprocity falls from 87.95 to 83.89 percent. Reciprocity is the fraction of positive arrows with a positive arrow back.

The largest component stays above 99.6 percent of accounts observed in positive ratings at each cutoff. The history remains almost entirely connected within that population. Keeping old ratings in a cumulative graph does not mean those opinions remained current.

**Sources / preparation:** outputs/flagship/structural_evolution.csv. Year-end snapshots, 2011–2015.

## 10. Who receives the next positive rating?

**Timing:** 60 seconds

The uniform benchmark gives each eligible recipient the same chance before a new rating. Candidates must already have appeared. We exclude the rater and accounts they have already rated positively. First-time recipients are outside this comparison.

The example on the left is invented. Two of ten candidates have at least 32 prior incoming ratings, so this group contributes two tenths to the expected count for that event. We add those probabilities over all eligible events.

The actual 32-plus group receives 7,356 ratings, compared with 579.4 expected. Their ratio is 12.7. That is a large difference from uniform choice, but it does not explain the reason.

**Sources / preparation:** outputs/temporal/target_choice_by_prior_degree.csv; scripts/temporal_analysis.py. Uniform comparison: 27,133 eligible events.

## 11. Matching reduces the benchmark gap

**Timing:** 60 seconds

The matched benchmark compares recipients with eligible users in similar observed-tenure and recent-activity groups. Tenure starts at the first positive record, not registration. Activity counts ratings given or received in the previous 90 days.

The 32-plus group's observed-to-expected ratio changes from 12.70 under uniform choice to 1.65 after matching. Much of the initial contrast is therefore sensitive to the benchmark.

Matching retains 99.48 percent of eligible events, so the event sets differ slightly. Activity also overlaps with accumulated degree. The remaining association does not prove that high prior ratings caused a user to be selected.

**Sources / preparation:** outputs/flagship/matched_target_choice.csv. Matched 32+ group: 7,294 observed / 4,424.5 expected; 26,993 retained events.

## 12. Connectivity depends on prominent users

**Timing:** 45 seconds

This experiment asks what happens if nodes are removed. Blue shows random removal, averaged over 30 runs. Orange removes accounts by their original degree, highest first.

After removing five percent, the largest component contains 87.6 percent of the original accounts under random removal, compared with 45.6 percent under targeted removal. Connectivity is more sensitive to losing prominent accounts.

All percentages use the original 5,881 accounts as the denominator, including 308 isolates. This is a hypothetical graph experiment. It is not evidence that users actually left or that trading would fail in this way.

**Sources / preparation:** outputs/robustness/node_removal_summary.csv. Target order is fixed using original projected degree, not recomputed after each deletion.

## 13. Checks that change the interpretation

**Timing:** 50 seconds

The first row changes the positive-rating threshold to at least plus five. The cumulative top one percent share still rises, from 16.3 to 19.3 percent.

The second row follows the same 1,631 accounts seen by the end of 2011. Their cumulative share also rises, from 15.5 to 22.2 percent. This includes ratings they receive from later entrants, and the top recipients are reselected at each cutoff.

The annual check changes the story: concentration falls after 2013. Our conclusions concern accumulated records and observed choices. Trade outcomes, visibility, and rating expiry are not in this file.

**Sources / preparation:** outputs/temporal/annual_snapshots_rating_ge5.csv; outputs/sensitivity/fixed_2011_cohort_concentration.csv; outputs/sensitivity/annual_only_concentration.csv.

## 14. Findings and code demonstration

**Timing:** 40 seconds, then a two-minute demonstration

Three findings answer our question. Triangle closure exceeds all three reference constructions. Cumulative rating concentration rises, while yearly concentration falls after 2013. The high-degree recipient contrast becomes much smaller after matching.

For the demonstration, we will inspect a rating record, show the positive directed graph and its undirected version, and reconstruct the annual versus cumulative counts. Then we will run the manifest checker.

The checker validates stored source, scripts, environment, and output consistency. The separate six-script runner performs the analyses. Neither is a guarantee that every scientific interpretation is correct.

**Sources / preparation:** presentation/DEMO.md; scripts/reproduce.py; python scripts/verify_reproduction.py --check-manifest. Repository: https://github.com/O-2wice/bitcoin-otc-trust-network-science

## 15. Sources and reproducibility

**Timing:** Backup for questions

Our data source is SNAP Bitcoin OTC and the accompanying Kumar paper. ER, BA, and Louvain provide the model and community-method foundations. NetworkX performs the numerical graph analysis; Cytoscape supplies the selected signed-network views.

The repository contains the source checksum, pinned environment, fixed seeds, analysis scripts, worked notebooks, outputs, and the execution manifest. To reproduce the numerical work, download the source and run all six scripts through reproduce.py, then check the manifest.

The report contains full references and graph definitions. The team must be able to explain the code and its limitations.

**Sources / preparation:** SNAP; Kumar et al. (2016); Erdős and Rényi (1959); Barabási and Albert (1999); Blondel et al. (2008). Full references in report/main.tex and README links.
