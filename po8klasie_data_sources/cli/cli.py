import click as click

from po8klasie_data_sources.cli.cli_logger import cli_logger


@click.group()
@click.pass_context
def cli(ctx):
    # ensure that ctx.obj exists and is a dict
    # (in case `cli()` is called without __name__ == "__main__")
    ctx.ensure_object(dict)


@cli.command("create_intermediate_files")
@click.argument("data_sources", nargs=-1)
@click.option("--environment", "-e")
@click.pass_obj
def create_intermediate_files_command(obj, environment, data_sources):
    """Create intermediate files"""
    from po8klasie_data_sources.cli.commands.create_intermediate_files import (
        create_intermediate_files,
    )

    obj["environment_manager"].load_environment(environment_string=environment)

    create_intermediate_files(
        environment_manager=obj["environment_manager"], data_sources_ids=data_sources
    )


@cli.command("create_records")
@click.argument("data_sources", nargs=-1)
@click.option("--environment", "-e")
@click.option("--override-intermediate-files-dir")
@click.pass_obj
def create_records_command(
    obj, environment, data_sources, override_intermediate_files_dir
):
    """Create records"""
    from po8klasie_data_sources.cli.commands.create_records import create_records

    obj["environment_manager"].load_environment(
        environment_string=environment,
        override_intermediate_files_dir=override_intermediate_files_dir,
    )

    create_records(
        environment_manager=obj["environment_manager"], data_sources_ids=data_sources
    )


@cli.command("init_projects")
@click.option("--environment", "-e")
@click.pass_obj
def init_projects_command(obj, environment):
    """Init projects"""
    from po8klasie_data_sources.cli.commands.init_projects import init_projects

    obj["environment_manager"].load_environment(environment_string=environment)

    init_projects(environment_manager=obj["environment_manager"])

    cli_logger.info("Created project records")


@cli.command("create_db_schema")
@click.option("--environment", "-e")
@click.pass_obj
def create_db_schema(obj, environment):
    """Create db schema"""
    from po8klasie_data_sources.db.db_regeneration_utils import create_all

    environment_manager = obj["environment_manager"]

    environment_manager.load_environment(environment_string=environment)

    create_all(environment_manager.db.get_engine())
    cli_logger.info("Created db schema")


@cli.command("drop_db")
@click.option("--environment", "-e")
@click.pass_obj
def drop_db_command(obj, environment):
    """Drop db data"""
    from po8klasie_data_sources.db.db_regeneration_utils import drop_all
    from termcolor import colored

    environment_manager = obj["environment_manager"]

    environment_manager.load_environment(environment_string=environment)

    cli_logger.warn(colored("!!! All DB data will be deleted !!!", "red"))
    if input("Do you wish to proceed? ") not in ["y", "yes"]:
        return

    drop_all(environment_manager.db.get_engine())
    cli_logger.info("Dropped db")


@cli.command("regenerate_db")
@click.option("--environment", "-e")
@click.option("--override-intermediate-files-dir")
@click.pass_context
def regenerate_db_command(ctx, environment, override_intermediate_files_dir):
    """Regenerate db"""
    ctx.invoke(drop_db_command, environment=environment)
    ctx.invoke(create_db_schema, environment=environment)
    ctx.invoke(init_projects_command, environment=environment)
    ctx.invoke(
        create_records_command,
        environment=environment,
        data_sources=["__all__"],
        override_intermediate_files_dir=override_intermediate_files_dir,
    )
