import click


@click.group(
    name="tize", context_settings=dict(auto_envvar_prefix="TIZE")
)
def tize():
    pass


@tize.command(name="hello")
def hello():
    click.echo("Hello world")
