"""Small, inspectable references for the teaching labs; no model or network calls."""
import json
import math
import numbers

import numpy as np

from twin import network, shortest


def paired_change(before, after, pixel_size_m, threshold):
    """Compare aligned pixel grids using only pixels valid on BOTH dates."""
    before, after = np.asarray(before, float), np.asarray(after, float)
    if before.ndim != 2 or before.shape != after.shape or not before.size:
        raise ValueError('Expected nonempty aligned 2D arrays of equal shape')
    if not math.isfinite(pixel_size_m) or pixel_size_m <= 0:
        raise ValueError('Pixel size must be positive and finite')
    if not math.isfinite(threshold) or threshold < 0:
        raise ValueError('Threshold must be nonnegative and finite')
    valid = np.isfinite(before) & np.isfinite(after)
    delta = np.full(before.shape, np.nan)
    delta[valid] = after[valid] - before[valid]
    loss = valid & (delta < -threshold)
    return dict(delta=delta, valid=valid, loss=loss,
                valid_pixels=int(valid.sum()), loss_pixels=int(loss.sum()),
                loss_area_m2=float(loss.sum() * pixel_size_m**2),
                mean_change=float(delta[valid].mean()) if valid.any() else None)


def access_summary(minutes, population, threshold_min):
    """Disconnected people remain in the denominator of service coverage."""
    minutes, population = np.asarray(minutes, float), np.asarray(population, float)
    if minutes.ndim != 1 or minutes.shape != population.shape:
        raise ValueError('Expected equal 1D travel and population arrays')
    if (not np.isfinite(population).all() or (population < 0).any()
            or population.sum() <= 0 or np.isnan(minutes).any() or (minutes < 0).any()):
        raise ValueError('Invalid population or travel times; +inf means disconnected')
    if not math.isfinite(threshold_min) or threshold_min < 0:
        raise ValueError('Invalid service threshold')
    reachable = np.isfinite(minutes)
    served = minutes <= threshold_min
    reachable_population = float(population[reachable].sum())
    return dict(coverage=float(population[served].sum() / population.sum()),
                unreachable_population=float(population[~reachable].sum()),
                mean_reachable_min=(float(np.average(minutes[reachable], weights=population[reachable]))
                                    if reachable_population else None))


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def strict_json(text):
    def reject_constant(value):
        raise ValueError('Nonstandard JSON number: ' + value)
    return json.loads(text, object_pairs_hook=_unique_object, parse_constant=reject_constant)


def grade_answer(text, expected, tolerances=None):
    """Exact keys/types; numeric tolerances declared BEFORE seeing an answer.

    A null expected value represents an explicitly unanswerable task.
    Wrong but well-typed answers count as schema-valid failures.
    """
    tolerances = tolerances or {}
    if any(not math.isfinite(t) or t < 0 for t in tolerances.values()):
        raise ValueError('Tolerances must be nonnegative and finite')
    try:
        answer = strict_json(text)
    except (ValueError, TypeError):
        return dict(schema_ok=False, passed=False, reason='Invalid or duplicate-key JSON')
    if not isinstance(answer, dict) or set(answer) != set(expected):
        return dict(schema_ok=False, passed=False, reason='Return exactly the requested keys')
    checks, errors = {}, {}
    for key, truth in expected.items():
        value = answer[key]
        if isinstance(truth, numbers.Real) and not isinstance(truth, bool):
            if type(value) not in (int, float) or not math.isfinite(value):
                return dict(schema_ok=False, passed=False, reason=f'{key}: expected finite number')
            errors[key] = abs(value - truth)
            checks[key] = errors[key] <= tolerances.get(key, 0)
        elif truth is None:
            # A fabricated answer to an unanswerable question is a semantic failure.
            checks[key] = value is None
        else:
            if type(value) is not type(truth):
                return dict(schema_ok=False, passed=False, reason=f'{key}: wrong type')
            checks[key] = value == truth
    return dict(schema_ok=True, passed=all(checks.values()), checks=checks, absolute_errors=errors)


def spatial_suite(seed=2026, count=30):
    """Return separate public cases and answer keys. Seeded tasks, not model results.

    Axis-aligned rectangle containment uses inclusive boundary semantics.
    Routing references Dijkstra on an explicitly supplied undirected graph.
    """
    if count < 1:
        raise ValueError('count must be positive')
    rng = np.random.default_rng(seed)
    cases, answers = [], {}
    for i in range(count):
        case_id = f'{seed}-{i:03d}'
        family = ['distance', 'routing', 'containment'][i % 3]
        if family == 'distance':
            points = rng.choice(21, size=8, replace=False).reshape(4, 2) * 100
            places = dict(zip('ABC', points[:3].tolist()))
            query = points[3].tolist()
            distances = {k: math.dist(v, query) for k, v in places.items()}
            nearest = min(distances, key=lambda k: (distances[k], k))
            expected = dict(nearest=nearest, distance_m=distances[nearest])
            tolerance = {'distance_m': 1.0}
            evidence = dict(places=places, query=query, units='metres', axes='east, north')
            task = 'Find the nearest place by Euclidean distance; break ties alphabetically. Return nearest and distance_m.'
        elif family == 'routing':
            nodes, graph = network(n=4, step=100.)
            edges = [(u, v) for u in graph for v, _ in graph[u] if u < v]
            blocked = [edge for edge in edges if rng.random() < .35]
            if i % 6 == 1:
                blocked += [(0, 1), (0, 4)]  # guaranteed disconnected cases
            nodes, graph = network(n=4, step=100., blocked=blocked)
            distance = float(shortest(graph, [0])[15])
            expected = dict(reachable=math.isfinite(distance),
                            distance_m=distance if math.isfinite(distance) else None)
            tolerance = {'distance_m': 1.0}
            evidence = dict(edges=[[u, v, w] for u in graph for v, w in graph[u] if u < v],
                            source=0, target=15, undirected=True, units='metres')
            task = 'Use ONLY listed edges. Return reachable (boolean) and shortest distance_m (number, or null if disconnected).'
        else:
            x, y = rng.integers(0, 10, 2) * 100
            width, height = rng.integers(1, 6, 2) * 100
            mode = (i // 3) % 3
            point = [int(x + width / 2), int(y + height / 2)]
            if mode == 1:
                point = [int(x), int(y)]  # boundary counts as inside
            if mode == 2:
                point = [int(x + width + 1), int(y)]
            expected = dict(inside=mode != 2)
            tolerance = {}
            evidence = dict(bounds=[int(x), int(y), int(x+width), int(y+height)], point=point,
                            bounds_order='xmin,ymin,xmax,ymax', units='metres')
            task = 'Is the point inside this closed rectangle? Boundary counts as inside. Return inside (boolean).'
        cases.append(dict(case_id=case_id, family=family, task=task, evidence=evidence,
                          tolerance=tolerance))
        answers[case_id] = expected
    return cases, answers


def grade_suite(response_text, cases, answers):
    """Grade all scheduled cases; missing/invalid responses never shrink denominator."""
    envelope_error = None
    try:
        submitted = strict_json(response_text)
        if not isinstance(submitted, dict):
            raise ValueError('Expected object keyed by case_id')
    except (TypeError, ValueError) as error:
        submitted = {}
        envelope_error = str(error)
    rows = []
    for case in cases:
        key = case['case_id']
        grade = grade_answer(json.dumps(submitted[key]), answers[key], case['tolerance']) if key in submitted else dict(
            schema_ok=False, passed=False, reason='Missing answer')
        rows.append(dict(case_id=key, family=case['family'], **grade))
    extra = sorted(set(submitted) - set(answers))
    return dict(total=len(rows), passed=sum(r['passed'] for r in rows),
                schema_valid=sum(r['schema_ok'] for r in rows),
                envelope_error=envelope_error, unexpected_ids=extra, rows=rows)
