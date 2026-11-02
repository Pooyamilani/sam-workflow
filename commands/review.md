# /review

Review only the current diff (`git diff`), not unrelated code.

Check: correctness, regression risk, edge cases, test coverage, security/data-loss
concerns where relevant, and unnecessary changes outside the diff's scope.

Keep output actionable and short. For over-engineering/simplicity concerns, defer to
ponytail's review commands instead of duplicating that analysis here.

## State-regression checks (UI changes)

A diff that works for the intended path can still break state the user controls. For every
effect/handler touched or removed, check:
- What re-triggers this effect? Any prop the parent derives from this component's own output
  (echo loop: child emits → parent stores → comes back as prop → effect reacts)?
- Does it call imperative setters (zoom/center/scroll/focus/reset/setValue) that would overwrite
  user-controlled state?
- Does removing code leave a now-wrong dependency array, stale closure, or duplicated listener?
- Does it behave in non-default state (zoomed, scrolled, filled form), in every mode (new/edit),
  and for every other consumer/template of the shared component?
If any is unverified, say so and recommend running the `browser-test` skill.
