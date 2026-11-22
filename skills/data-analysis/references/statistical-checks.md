# Statistical and Modelling Checks

## Descriptive work
- Report the sample size with every statistic. Use medians and quantiles alongside means for skewed data.
- Plot or tabulate distributions before summarizing them; check for heavy tails, multimodality and spikes at sentinel values (0, -1, 999, empty strings).
- When comparing groups, check that their composition is comparable. Simpson's paradox appears when segment mix differs.

## Inference
- State the hypothesis, test and significance threshold before looking at results.
- Check the test's assumptions (independence, distribution shape, equal variance) or use a robust or nonparametric alternative, or a bootstrap.
- Report effect sizes with confidence intervals, not only p-values. Distinguish statistical significance from practical importance.
- Correct for multiple comparisons when testing many metrics or segments, or label the findings exploratory.
- Avoid peeking: repeated testing of an experiment while it runs inflates false positives unless a sequential method is used.

## Experiments (A/B tests)
- Verify randomization: check sample-ratio mismatch and pre-period balance of key covariates.
- Analyze at the unit of randomization; cluster or aggregate when units are not independent.
- Watch for novelty effects, interference between units, and changes in the metric's definition.

## Model evaluation

- Choose an evaluation split that reflects how the software will be used. Keep test inputs separate from training and preprocessing.
- Compare with a simple baseline using the same inputs, units and scoring method.
- Report the score, its spread, the number of observations and any exclusions. Identify conditions where the metric becomes unreliable.
- Record the evaluation command, software versions and any random seed needed to reproduce it.

## Time series
- Check for missing timestamps, duplicates, time-zone shifts, daylight-saving artifacts and changes in the collection process.
- Account for trend and seasonality before calling a point anomalous; compare against the same period in earlier cycles.

## Anomalies
- Define "normal" from a relevant reference (peers, history, expected range) before labelling something anomalous.
- Check for late inputs, duplicates, schema changes and changes of unit before interpreting unexpected output.
