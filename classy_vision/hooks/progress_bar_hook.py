#!/usr/bin/env python3

from typing import Any, Dict, Optional

from classy_vision.generic.distributed_util import is_master
from classy_vision.hooks.classy_hook import ClassyHook
from classy_vision.state.classy_state import ClassyState


try:
    import progressbar

    progressbar_available = True
except ImportError:
    progressbar_available = False


class ProgressBarHook(ClassyHook):
    """
    Displays a progress bar to show progress in processing batches.
    """

    on_rendezvous = ClassyHook._noop
    on_start = ClassyHook._noop
    on_sample = ClassyHook._noop
    on_forward = ClassyHook._noop
    on_loss = ClassyHook._noop
    on_backward = ClassyHook._noop
    on_end = ClassyHook._noop

    def __init__(self) -> None:
        self.progress_bar: Optional[progressbar.ProgressBar] = None
        self.bar_size: int = 0
        self.batches: int = 0

    def on_phase_start(
        self, state: ClassyState, local_variables: Dict[str, Any]
    ) -> None:
        """
        Create and display a progress bar with 0 progress.
        """
        if not progressbar_available:
            raise RuntimeError(
                "progressbar module not installed, cannot use ProgressBarHook"
            )

        if is_master():
            self.bar_size = state.num_batches_per_phase
            self.batches = 0
            self.progress_bar = progressbar.ProgressBar(self.bar_size)
            self.progress_bar.start()

    def on_update(self, state: ClassyState, local_variables: Dict[str, Any]) -> None:
        """
        Update the progress bar with the batch size.
        """
        if is_master() and self.progress_bar is not None:
            self.batches += 1
            self.progress_bar.update(min(self.batches, self.bar_size))

    def on_phase_end(self, state: ClassyState, local_variables: Dict[str, Any]) -> None:
        """
        Clear the progress bar at the end of the phase.
        """
        if is_master() and self.progress_bar is not None:
            self.progress_bar.finish()