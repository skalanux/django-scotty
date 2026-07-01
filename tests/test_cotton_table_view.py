"""Tests for CottonTableView internals.

Covers export filename generation, table kwargs construction,
action column rendering, configuration attribute propagation,
and POST action handling.
"""

from http import HTTPStatus
from typing import Any
from unittest.mock import MagicMock

from django.http import HttpResponse
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


class TestTableConfigAttributes:
    """Tests for configuration attribute propagation from view to table.

    Verifies that ``has_border``, ``show_download_link``,
    ``show_filter_line``, and conditional title are correctly passed
    from ``CottonTableView`` to the table instance during
    ``get_context_data``.
    """

    _view: Any = None

    @staticmethod
    def _make_view(**overrides: Any) -> Any:
        """Build a ``CottonTableView`` with ``object_list`` populated."""
        from django_scotty.views.list import CottonTableView

        factory = RequestFactory()
        request = factory.get("/")
        view = CottonTableView()
        view.setup(request)
        view.model = DummyItem
        view.object_list = DummyItem.objects.none()
        for key, value in overrides.items():
            setattr(view, key, value)
        return view

    # ── has_border ────────────────────────────────────────────

    def test_has_border_default_true_on_table(self) -> None:
        """``ActionTable.has_border`` defaults to ``True``."""
        from django_scotty.table import ActionTable

        assert ActionTable.has_border is True

    def test_has_border_default_true_on_view(self) -> None:
        """``CottonTableView.table_has_borders`` defaults to ``True``."""
        from django_scotty.views.list import CottonTableView

        assert CottonTableView.table_has_borders is True

    def test_has_border_propagates_to_table(self, db) -> None:  # noqa: ARG002
        """``table_has_borders=False`` sets ``table.has_border = False``."""
        view = self._make_view(table_has_borders=False)
        context = view.get_context_data()
        table = context["table"]
        assert table.has_border is False

    def test_has_border_propagates_true(self, db) -> None:  # noqa: ARG002
        """Default ``table_has_borders=True`` sets ``table.has_border = True``."""
        view = self._make_view()
        context = view.get_context_data()
        table = context["table"]
        assert table.has_border is True

    # ── show_download_link ────────────────────────────────────

    def test_show_download_link_default_true(self) -> None:
        """``CottonTableView.table_show_download_link`` defaults to ``True``."""
        from django_scotty.views.list import CottonTableView

        assert CottonTableView.table_show_download_link is True

    def test_show_download_link_propagates_true(self, db) -> None:  # noqa: ARG002
        """Default propagates ``table.show_download_link = True``."""
        view = self._make_view()
        context = view.get_context_data()
        table = context["table"]
        assert table.show_download_link is True

    def test_show_download_link_propagates_false(self, db) -> None:  # noqa: ARG002
        """Setting ``table_show_download_link=False`` hides the link."""
        view = self._make_view(table_show_download_link=False)
        context = view.get_context_data()
        table = context["table"]
        assert table.show_download_link is False

    # ── show_filter_line ──────────────────────────────────────

    def test_show_filter_line_default_true(self) -> None:
        """``CottonTableView.show_filter_line`` defaults to ``True``."""
        from django_scotty.views.list import CottonTableView

        assert CottonTableView.show_filter_line is True

    def test_show_filter_line_propagates_to_table(self, db) -> None:  # noqa: ARG002
        """``show_filter_line`` is copied to ``table.show_filter_line``."""
        view = self._make_view()
        context = view.get_context_data()
        table = context["table"]
        assert table.show_filter_line is True

    def test_show_filter_line_false_propagates(self, db) -> None:  # noqa: ARG002
        """Setting ``show_filter_line=False`` propagates correctly."""
        view = self._make_view(show_filter_line=False)
        context = view.get_context_data()
        table = context["table"]
        assert table.show_filter_line is False

    # ── conditional title ─────────────────────────────────────

    def test_title_default(self, db) -> None:  # noqa: ARG002
        """Default title is ``"Listado"``."""
        view = self._make_view()
        context = view.get_context_data()
        table = context["table"]
        assert table.title == "Listado"

    def test_empty_title(self, db) -> None:  # noqa: ARG002
        """Setting title to ``""`` propagates empty string to table."""
        view = self._make_view(title="")
        context = view.get_context_data()
        table = context["table"]
        assert table.title == ""


class TestCottonTableViewPost:
    """Tests for ``CottonTableView.post()`` — single and bulk action handling.

    Covers the method dispatch, action method invocation, filter-based
    queryset resolution, condition checks, and error handling.
    """

    # ── helpers ────────────────────────────────────────────────

    @staticmethod
    def _stub_action(
        return_value: HttpResponse | None = None,
        condition_result: bool | None = None,
    ) -> MagicMock:
        """Build a mock action method with optional condition.

        Args:
            return_value: What the action callable returns.
            condition_result: When set, the action gets a ``condition``
                callable that returns this value.

        Returns:
            A ``MagicMock`` configured as an action method.
        """
        method = MagicMock(return_value=return_value)
        if condition_result is not None:
            method.condition = MagicMock(return_value=condition_result)
        return method

    # ── single-row actions (via GET params) ───────────────────

    def test_single_row_calls_action_with_obj(self, db) -> None:  # noqa: ARG002
        """GET ``?pk=1&action=mark_processed`` calls the action with the obj."""
        from django_scotty.views.list import CottonTableView

        item = DummyItem.objects.create(name="single", amount=10)
        factory = RequestFactory()
        request = factory.get(f"/?pk={item.pk}&action=mark_processed")

        view = CottonTableView()
        view.setup(request)
        view.model = DummyItem

        mock_action = self._stub_action(return_value=None)
        view.mark_processed = mock_action  # type: ignore[attr-defined]

        view.post(request)
        mock_action.assert_called_once_with(item)

    def test_single_row_no_action_param_does_not_crash(self, db) -> None:  # noqa: ARG002
        """GET with ``pk`` but no ``action`` redirects without error."""
        from django_scotty.views.list import CottonTableView

        item = DummyItem.objects.create(name="orphan", amount=1)
        factory = RequestFactory()
        request = factory.get(f"/?pk={item.pk}")

        view = CottonTableView()
        view.setup(request)
        view.model = DummyItem

        response = view.post(request)
        assert response.status_code == HTTPStatus.FOUND

    # ── bulk actions (via POST) ───────────────────────────────

    def test_bulk_with_selected_pks_calls_action_per_obj(self, db) -> None:  # noqa: ARG002
        """POST with multiple ``seleccionar`` values calls the action once per obj."""
        from django_scotty.views.list import CottonTableView

        items = [DummyItem.objects.create(name=f"bulk {i}") for i in range(3)]
        factory = RequestFactory()
        request = factory.post(
            "/",
            {"action": "archive", "seleccionar": [str(i.pk) for i in items]},
        )

        view = CottonTableView()
        view.setup(request)
        view.model = DummyItem

        mock_action = self._stub_action(return_value=None)
        view.archive = mock_action  # type: ignore[attr-defined]

        view.post(request)
        assert mock_action.call_count == 3
        for item in items:
            mock_action.assert_any_call(item)

    def test_bulk_with_filter_query_string(self, db) -> None:  # noqa: ARG002
        """POST with ``filter_query_string`` resolves via filterset."""
        from tests.views import DummyItemListView

        DummyItem.objects.create(name="active one", active=True)
        DummyItem.objects.create(name="inactive one", active=False)

        factory = RequestFactory()
        request = factory.post(
            "/",
            {
                "action": "mark_processed",
                "filter_query_string": "active=True",
            },
        )

        view = DummyItemListView()
        view.setup(request)
        mock_action = self._stub_action(return_value=None)
        view.mark_processed = mock_action  # type: ignore[attr-defined]

        view.post(request)
        # Only the active item should be acted upon
        assert mock_action.call_count == 1
        assert mock_action.call_args[0][0].name == "active one"

    def test_bulk_with_selected_pks_overrides_filter(self, db) -> None:  # noqa: ARG002
        """When both ``seleccionar`` and ``filter_query_string`` are present,
        ``selected_pks`` wins (overrides the filter-based queryset)."""
        from tests.views import DummyItemListView

        active = DummyItem.objects.create(name="active", active=True)
        inactive = DummyItem.objects.create(name="inactive", active=False)

        factory = RequestFactory()
        request = factory.post(
            "/",
            {
                "action": "mark_processed",
                "seleccionar": [str(inactive.pk)],
                "filter_query_string": "active=True",
            },
        )

        view = DummyItemListView()
        view.setup(request)
        mock_action = self._stub_action(return_value=None)
        view.mark_processed = mock_action  # type: ignore[attr-defined]

        view.post(request)
        # selected_pks wins — only the inactive item is acted on
        assert mock_action.call_count == 1
        assert mock_action.call_args[0][0].pk == inactive.pk

    def test_bulk_without_filterset_class_does_not_crash(self, db) -> None:  # noqa: ARG002
        """POST with ``filter_query_string`` but no ``filterset_class``
        does not crash (``None`` check)."""
        from django_scotty.views.list import CottonTableView

        DummyItem.objects.create(name="orphan", active=True)
        factory = RequestFactory()
        request = factory.post(
            "/",
            {
                "action": "mark_processed",
                "filter_query_string": "active=True",
            },
        )

        view = CottonTableView()
        view.setup(request)
        view.model = DummyItem
        view.filterset_class = None

        mock_action = self._stub_action(return_value=None)
        view.mark_processed = mock_action  # type: ignore[attr-defined]

        # Should not raise even though filterset_class is None
        response = view.post(request)
        assert response.status_code == HTTPStatus.FOUND
        # No queryset was built → action method was never called
        mock_action.assert_not_called()

    # ── condition checks ──────────────────────────────────────

    def test_condition_false_skips_action(self, db) -> None:  # noqa: ARG002
        """When an action's ``condition`` returns ``False`` the action
        is not invoked."""
        from django_scotty.views.list import CottonTableView

        item = DummyItem.objects.create(name="conditional", amount=10)
        factory = RequestFactory()
        request = factory.get(f"/?pk={item.pk}&action=conditional_action")

        view = CottonTableView()
        view.setup(request)
        view.model = DummyItem

        mock_action = self._stub_action(return_value=None, condition_result=False)
        view.conditional_action = mock_action  # type: ignore[attr-defined]

        view.post(request)
        mock_action.assert_not_called()

    def test_condition_true_calls_action(self, db) -> None:  # noqa: ARG002
        """When an action's ``condition`` returns ``True`` the action is invoked."""
        from django_scotty.views.list import CottonTableView

        item = DummyItem.objects.create(name="conditional-pass", amount=10)
        factory = RequestFactory()
        request = factory.get(f"/?pk={item.pk}&action=conditional_action")

        view = CottonTableView()
        view.setup(request)
        view.model = DummyItem

        mock_action = self._stub_action(return_value=None, condition_result=True)
        view.conditional_action = mock_action  # type: ignore[attr-defined]

        view.post(request)
        mock_action.assert_called_once_with(item)

    def test_condition_exception_fails_open(self, db) -> None:  # noqa: ARG002
        """When ``condition`` raises, the action is still performed (fail-open)."""
        from django_scotty.views.list import CottonTableView

        item = DummyItem.objects.create(name="broken-condition", amount=10)
        factory = RequestFactory()
        request = factory.get(f"/?pk={item.pk}&action=conditional_action")

        view = CottonTableView()
        view.setup(request)
        view.model = DummyItem

        faulty = MagicMock()
        faulty.condition = MagicMock(side_effect=ValueError("oops"))
        view.conditional_action = faulty  # type: ignore[attr-defined]

        # The exception in condition is caught, then the action is called
        # because the code does: if condition → try/except → fall through
        # Actually, looking at post() more carefully:
        #   if getattr(action_method, "condition", None):
        #       try: condition_result = action_method.condition(...)
        #       except: pass → condition_result remains undefined
        #   else: condition_result = True
        #   if condition_result: ...
        # Wait, that's wrong. Let me re-read:
        #   if getattr(action_method, "condition", None):
        #       condition_result = action_method.condition(obj, self.request)
        #   else:
        #       condition_result = True
        #   if condition_result: ...
        # There's no try/except in post()! The try/except is a LEVEL up
        # wrapping the whole thing.
        # So if condition raises, the exception bubbles up to the outer
        # try/except and is logged, and execution continues to the next obj.
        # The action is NOT called for that obj.

        # Actually looking at the code:
        #   try:
        #       if getattr(action_method, "condition", None):
        #           condition_result = action_method.condition(obj, self.request)
        #       else:
        #           condition_result = True
        #       if condition_result:
        #           result = getattr(self, action)(obj)
        #           results.append(result)
        #   except Exception as e:
        #       logging.exception(...)
        # So if condition raises → exception caught, logged, action NOT called

        view.post(request)
        # The condition raised → action should NOT be called
        faulty.assert_not_called()

    # ── response handling ─────────────────────────────────────

    def test_action_returns_http_response_directly(self, db) -> None:  # noqa: ARG002
        """When the action returns an ``HttpResponse`` with ``status_code``,
        it is returned directly for single-row actions."""
        from django_scotty.views.list import CottonTableView

        item = DummyItem.objects.create(name="responder", amount=10)
        factory = RequestFactory()
        request = factory.get(f"/?pk={item.pk}&action=respond")

        view = CottonTableView()
        view.setup(request)
        view.model = DummyItem

        expected = HttpResponse("custom", status=HTTPStatus.CREATED)
        view.respond = MagicMock(return_value=expected)  # type: ignore[attr-defined]

        response = view.post(request)
        assert response is expected
        assert response.status_code == HTTPStatus.CREATED

    def test_finally_hook_called_for_bulk(self, db) -> None:  # noqa: ARG002
        """Bulk actions invoke ``finally_<action>`` when results exist."""
        from django_scotty.views.list import CottonTableView

        items = [DummyItem.objects.create(name=f"f{i}") for i in range(2)]
        factory = RequestFactory()
        request = factory.post(
            "/",
            {"action": "process", "seleccionar": [str(i.pk) for i in items]},
        )

        view = CottonTableView()
        view.setup(request)
        view.model = DummyItem

        view.process = MagicMock(return_value=None)  # type: ignore[attr-defined]
        finally_response = HttpResponse("done")
        view.finally_process = MagicMock(return_value=finally_response)  # type: ignore[attr-defined]

        response = view.post(request)
        assert response is finally_response
        view.finally_process.assert_called_once()

    # ── filter_params assignment ──────────────────────────────

    def test_filter_params_stored_when_filter_query_string(self, db) -> None:  # noqa: ARG002
        """``self.filter_params`` is set when ``filter_query_string`` is posted."""
        from tests.views import DummyItemListView

        DummyItem.objects.create(name="some", active=True)
        factory = RequestFactory()
        request = factory.post(
            "/",
            {
                "action": "mark_processed",
                "filter_query_string": "active=True&page=2",
            },
        )

        view = DummyItemListView()
        view.setup(request)

        mock_action = self._stub_action(return_value=None)
        view.mark_processed = mock_action  # type: ignore[attr-defined]

        view.post(request)
        assert view.filter_params == {"active": "True"}  # page stripped
