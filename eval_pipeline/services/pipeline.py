import threading

from loguru import logger

from eval_pipeline.services.runner import EvalPipelineRunner
from eval_pipeline.services.scorer import Scorer


class PipelineService:
    _sessions: dict[str, dict] = {}

    @classmethod
    def start_run(cls, case_names: list[str]) -> str:
        runner = EvalPipelineRunner(
            case_names=case_names,
            on_case_started=lambda case_name: cls._mark_case_started(
                runner.session_id, case_name
            ),
            on_case_done=lambda case_name: cls._mark_case_done(
                runner.session_id, case_name
            ),
        )
        session_id = runner.session_id

        cls._sessions[session_id] = {
            "overall": "running",
            "cases": {name: "pending" for name in case_names},
        }

        threading.Thread(
            target=cls._execute, args=(session_id, runner), daemon=True
        ).start()

        return session_id

    @classmethod
    def get_status(cls, session_id: str) -> dict:
        return cls._sessions.get(session_id, {"overall": "unknown", "cases": {}})

    @classmethod
    def get_session(cls, session_id: str) -> dict | None:
        return cls._sessions.get(session_id)

    @classmethod
    def _mark_case_started(cls, session_id: str, case_name: str) -> None:
        cls._sessions[session_id]["cases"][case_name] = "started"

    @classmethod
    def _mark_case_done(cls, session_id: str, case_name: str) -> None:
        cls._sessions[session_id]["cases"][case_name] = "done"

    @classmethod
    def _execute(cls, session_id: str, runner: EvalPipelineRunner) -> None:
        try:
            runner.run()
            logger.info(
                f"Runner concluído. Iniciando scorer para session={session_id}."
            )
            Scorer(session_id).run()
            cls._sessions[session_id]["overall"] = "done"
            logger.success(f"Sessão {session_id} finalizada.")
        except Exception as exc:
            logger.error(f"Erro na sessão {session_id}: {exc}")
            cls._sessions[session_id]["overall"] = "error"
