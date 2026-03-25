import traceback

from video_system.actions.analysis import excel_rename, keyword_sort, stats_analysis
from video_system.actions.automation import pipeline_move, videofusion_merge_action
from video_system.actions.classification import aspect_sort, duration_sort
from video_system.actions.common import failure_response, load_catalog
from video_system.actions.file_management import (
    collect_files,
    flat_move,
    group_move,
    parent_prefix_rename,
    timestamp_rename,
)
from video_system.core.utils import ParameterValidationError


ACTION_HANDLERS = {
    "collect_files": collect_files,
    "group_move": group_move,
    "flat_move": flat_move,
    "parent_prefix_rename": parent_prefix_rename,
    "timestamp_rename": timestamp_rename,
    "aspect_sort": aspect_sort,
    "duration_sort": duration_sort,
    "stats_analysis": stats_analysis,
    "keyword_sort": keyword_sort,
    "excel_rename": excel_rename,
    "pipeline_move": pipeline_move,
    "videofusion_merge": videofusion_merge_action,
}


def dispatch_action(action_id, params):
    handler = ACTION_HANDLERS.get(action_id)
    if handler is None:
        return failure_response(f"unknown action: {action_id}")
    try:
        return handler(params or {})
    except ParameterValidationError as exc:
        return failure_response(str(exc))
    except Exception:
        return failure_response("service execution failed", traceback.format_exc())
