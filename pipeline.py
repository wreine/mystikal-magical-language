
from scanner import Kind, scan
from weaver import weave
from caster import TIME_LIMIT, cast


class Spell:
    """One spell moving through the pipeline. Its data is private."""

    def __init__(self, source):
        self._source = source
        self._runes = None
        self._weaving = None
        self._report = None
        self._problem = None

    # ----- getters: read the private data -----
    def get_source(self):
        return self._source

    def get_runes(self):
        return self._runes

    def get_weaving(self):
        return self._weaving

    def get_python(self):
        if self._weaving is None:
            return ""
        return self._weaving.python

    def get_report(self):
        return self._report

    def get_problem(self):
        return self._problem

    def is_empty(self):
        """True when there is only spaces and comments (nothing to cast)."""
        if self._runes is None:
            return self._source.strip() == ""
        for rune in self._runes:
            if rune.kind != Kind.GAP and rune.kind != Kind.NOTE:
                return False
        return True

    # ----- setters: the only way to change the private data -----
    def set_runes(self, runes):
        self._runes = runes

    def set_weaving(self, weaving):
        self._weaving = weaving

    def set_report(self, report):
        self._report = report

    def set_problem(self, problem):
        self._problem = problem


class Stage:
    """ABSTRACTION: the general idea of a step. It only promises run()."""

    label = "Stage"

    def run(self, spell):
        raise NotImplementedError("Dapat i-define ng bawat stage ang run()")

    def describe(self):
        return self.label + ": walang paglalarawan"


class ScannerStage(Stage):
    """INHERITANCE: ScannerStage is a Stage."""

    label = "Scanner"

    def run(self, spell):
        outcome = scan(spell.get_source())
        if outcome.problem is not None:
            spell.set_problem(outcome.problem)
        else:
            spell.set_runes(outcome.runes)

    def describe(self):
        return "Scanner: binabasa ang teksto at ginagawang runes"


class WeaverStage(Stage):
    label = "Weaver"

    def run(self, spell):
        if spell.get_runes() is None:
            return
        spell.set_weaving(weave(spell.get_runes()))

    def describe(self):
        return "Weaver: pinapalitan ang spells ng Python"


class CasterStage(Stage):
    label = "Caster"

    def __init__(self, time_limit=TIME_LIMIT):
        self._time_limit = TIME_LIMIT        # private
        self.set_time_limit(time_limit)      # goes through the checking method

    def get_time_limit(self):
        return self._time_limit

    def set_time_limit(self, seconds):
        """ENCAPSULATION: the value is checked before it is saved."""
        if seconds <= 0:
            raise ValueError("Ang time limit ay dapat higit sa 0 segundo")
        self._time_limit = seconds

    def run(self, spell):
        weaving = spell.get_weaving()
        if weaving is None:
            return
        spell.set_report(cast(weaving.python, weaving.line_map, self._time_limit))

    def describe(self):
        return "Caster: pinapatakbo ang Python (limitasyon: " + str(self._time_limit) + "s)"


class SpellPipeline:
    """POLYMORPHISM: runs any Stage with stage.run() without checking which one it is."""

    def __init__(self, time_limit=TIME_LIMIT):
        self._compile_stages = [ScannerStage(), WeaverStage()]
        self._cast_stage = CasterStage(time_limit)

    def get_stages(self):
        return self._compile_stages + [self._cast_stage]

    def compile(self, spell):
        """Scan, then weave. Stops at the first problem."""
        for stage in self._compile_stages:
            if spell.get_problem() is not None:
                break
            stage.run(spell)
        return spell

    def cast(self, spell):
        """Run the translated Python (called from a background thread)."""
        self._cast_stage.run(spell)
        return spell