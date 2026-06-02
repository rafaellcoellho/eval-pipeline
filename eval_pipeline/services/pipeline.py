import threading

from loguru import logger

from eval_pipeline.services.runner import EvalPipelineRunner
from eval_pipeline.services.scorer import Scorer

_TERMINAL_CASE_STATUSES = {"done", "error", "Falhou", "Cancelado", "Finalizado"}


class PipelineService:
    _sessions: dict[str, dict] = {}
    _runners: dict[str, EvalPipelineRunner] = {}

    @classmethod
    def start_run(cls, case_names: list[str]) -> str:
        runner = EvalPipelineRunner(
            case_names=case_names,
            on_case_status_changed=lambda case_name, status: cls._set_case_status(
                runner.session_id, case_name, status
            ),
            on_case_done=lambda case_name: cls._set_case_status(
                runner.session_id, case_name, "done"
            ),
            on_case_error=lambda case_name: cls._set_case_status(
                runner.session_id, case_name, "error"
            ),
        )
        session_id = runner.session_id

        cls._sessions[session_id] = {
            "overall": "running",
            "cases": {name: "pending" for name in case_names},
        }
        cls._runners[session_id] = runner

        threading.Thread(
            target=cls._execute, args=(session_id, runner), daemon=True
        ).start()

        return session_id

    @classmethod
    def stop_session(cls, session_id: str) -> None:
        runner = cls._runners.get(session_id)
        if runner:
            runner.stop(run_scorer_after=False)
        cls._cancel_pending_cases(session_id)
        cls._sessions[session_id]["overall"] = "cancelled"

    @classmethod
    def stop_and_analyze(cls, session_id: str) -> None:
        runner = cls._runners.get(session_id)
        if runner:
            runner.stop(run_scorer_after=True)
        cls._cancel_pending_cases(session_id)

    @classmethod
    def get_status(cls, session_id: str) -> dict:
        return cls._sessions.get(session_id, {"overall": "unknown", "cases": {}})

    @classmethod
    def get_session(cls, session_id: str) -> dict | None:
        return cls._sessions.get(session_id)

    @classmethod
    def _set_case_status(cls, session_id: str, case_name: str, status: str) -> None:
        cls._sessions[session_id]["cases"][case_name] = status

    @classmethod
    def _cancel_pending_cases(cls, session_id: str) -> None:
        cases = cls._sessions.get(session_id, {}).get("cases", {})
        for case_name, status in cases.items():
            if status not in _TERMINAL_CASE_STATUSES:
                cases[case_name] = "Cancelado"

    @classmethod
    def _execute(cls, session_id: str, runner: EvalPipelineRunner) -> None:
        try:
            runner.run()

            if runner.stop_event.is_set():
                if runner.run_scorer_after_stop:
                    logger.info(
                        f"Parando e analisando. Iniciando scorer para session={session_id}."
                    )
                    Scorer(session_id).run()
                    cls._sessions[session_id]["overall"] = "done"
                    logger.success(f"Sessão {session_id} finalizada (parcial).")
                return

            logger.info(
                f"Runner concluído. Iniciando scorer para session={session_id}."
            )
            Scorer(session_id).run()
            cls._sessions[session_id]["overall"] = "done"
            logger.success(f"Sessão {session_id} finalizada.")
        except Exception as exc:
            logger.error(f"Erro na sessão {session_id}: {exc}")
            cls._sessions[session_id]["overall"] = "error"
