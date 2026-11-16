import logging


def configurar_log(nivel: int = logging.INFO) -> None:
    """Chamado só no ponto de entrada (main)."""
    logging.basicConfig(level=nivel, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
