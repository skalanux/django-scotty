"""Tests for CottonTableView internals.

Covers export filename generation, table kwargs construction, and
action column rendering.
"""

from unittest.mock import MagicMock

from django.test import RequestFactory

from tests.models import DummyItem


class SampleFilterSet:
    """A minimal filterset wrapper that delegates to django-filter's FilterSet.

    Used as a lightweight stand-in for filter integration tests.
    """

    class Meta:
        model = DummyItem
        fields = ["name", "active"]

    def __init__(self, *args, **kwargs):
        """Initialize the underlying django-filter FilterSet.

        Args:
            *args: Positional arguments forwarded to FilterSet.
            **kwargs: Keyword arguments forwarded to FilterSet.
        """
        from django_filters import FilterSet

        self._filterset = FilterSet(*args, **kwargs)

    def __getattr__(self, name):
        """Delegate attribute access to the underlying FilterSet.

        Args:
            name: The attribute name.

        Returns:
            Any: The attribute from the inner FilterSet.
        """
        return getattr(self._filterset, name)


class TestCottonTableViewGetExportFilename:
    """Tests for ``CottonTableView.get_export_filename``."""

    def test_generates_filename(self):
        """Verify the export filename matches the default slug pattern."""
        from django_scotty.views.list import CottonTableView

        filename = CottonTableView().get_export_filename("xlsx")
        assert filename == "cottontable.xlsx"


class TestCottonTableViewGetTableKwargs:
    """Tests for ``CottonTableView.get_table_kwargs``."""

    def test_default_not_view_only(self):
        """Verify table kwargs include ``post_paginate_hook`` by default."""
        from django_scotty.views.list import CottonTableView

        factory = RequestFactory()
        request = factory.get("/")
        view = CottonTableView()
        view.setup(request)
        view.model = DummyItem

        kwargs = view.get_table_kwargs()
        assert "post_paginate_hook" in kwargs


class TestActionTableRenderAcciones:
    """Tests for ``ActionTable.render_acciones`` dropdown logic.

    Verifies the actions dropdown is only rendered when at least one
    custom action passes its ``condition`` check.
    """

    def _action_method(self, condition_result: bool) -> MagicMock:
        """Create a mock action method with a ``condition`` callable.

        Args:
            condition_result: The value the condition should return.

        Returns:
            A MagicMock configured with a ``show_confirm`` attribute
            and a ``condition`` that returns ``condition_result``.
        """
        method = MagicMock()
        method.show_confirm = False
        method.condition = MagicMock(return_value=condition_result)
        return method

    def test_skips_dropdown_when_all_conditions_false(self) -> None:
        """Verify the actions dropdown is omitted when all conditions fail.

        Two custom actions are configured but both have conditions that
        return False. The rendered output must not contain any dropdown
        markup.
        """
        from django_scotty.table import ActionTable

        view = MagicMock()
        view.mark_processed = self._action_method(False)
        view.archive = self._action_method(False)

        table = ActionTable(
            [],
            available_actions=[
                ("mark_processed", "Mark Processed", True, True, False),
                ("archive", "Archive", True, True, False),
            ],
        )
        table.view = view
        table.url_action_method = "list-view-dummyitem"

        class _Record:
            pk = 1

        result = table.render_acciones(_Record())
        assert "dropdown-toggle" not in result
        assert "dropdown-menu" not in result

    def test_shows_dropdown_when_some_conditions_pass(self) -> None:
        """Verify the actions dropdown appears when at least one condition passes.

        Two custom actions: one condition passes, one fails. The dropdown
        must be rendered with the passing action visible.
        """
        from django_scotty.table import ActionTable

        view = MagicMock()
        view.mark_processed = self._action_method(True)
        view.archive = self._action_method(False)

        table = ActionTable(
            [],
            available_actions=[
                ("mark_processed", "Mark Processed", True, True, False),
                ("archive", "Archive", True, True, False),
            ],
        )
        table.view = view
        table.url_action_method = "list-view-dummyitem"

        class _Record:
            pk = 1

        result = table.render_acciones(_Record())
        assert "dropdown-toggle" in result
        assert "dropdown-menu" in result
        assert "Mark Processed" in result
        assert "Archive" not in result

    def test_shows_dropdown_when_condition_raises(self) -> None:
        """Verify the action is shown (fail-open) when its condition raises.

        When a condition callable raises an exception, the code should
        still render the action rather than silently hiding it. This
        prevents a broken condition from making an action unreachable.
        """
        from django_scotty.table import ActionTable

        faulty = MagicMock()
        faulty.show_confirm = False
        faulty.condition = MagicMock(side_effect=ValueError("oops"))

        view = MagicMock()
        view.mark_processed = self._action_method(True)
        view.faulty = faulty

        table = ActionTable(
            [],
            available_actions=[
                ("mark_processed", "Mark Processed", True, True, False),
                ("faulty", "Faulty", True, True, False),
            ],
        )
        table.view = view
        table.url_action_method = "list-view-dummyitem"

        class _Record:
            pk = 1

        result = table.render_acciones(_Record())
        assert "dropdown-toggle" in result
        assert "dropdown-menu" in result
        assert "Faulty" in result
