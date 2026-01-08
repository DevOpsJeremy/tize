import click


@click.group(
    name="pycli-template", context_settings=dict(auto_envvar_prefix="PYCLI_TEMPLATE")
)
def pycli_template():
    pass


@pycli_template.command(name="hello")
def hello():
    click.echo("Hello world")
