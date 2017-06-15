import click


@click.group()
def cli():
    """Peachy"""
    pass


# @cli.command()
# def build():
#     """Build project executable."""
#     # PyInstaller
#     print('TODO')


# @cli.command()
# @click.option('--outputfile', type=str)
# def profile():
#     """Run profiler."""
#     print('Run Profiler')


@cli.command()
@click.option('--name', prompt='Project Name', type=str)
@click.option('--author', prompt='Author Name', type=str, default='')
@click.option('--email', prompt='Author Email', type=str, default='')
@click.option('--url', prompt='Project URL', type=str, default='')
@click.option('--main', prompt='Main script name', type=str,
              default='main.py')
@click.option('--assets', prompt='Name of assets directory', type=str,
              default='assets')
@click.option('--repo', prompt='Create a git repo', type=bool, default='n')
def createproject(name, author, email, url, main, assets, repo):
    """Create a new project."""
    # asset_directory name
    # Create git repo?
    '''scaffold
        .gitignore
        build.py
        config.json
        main.py
        game/
            assets/
            __init__.py
            __main__.py
    '''
    package_name = name.lower().replace(' ', '_')
    package_name = click.prompt('Package Name', type=str, default=package_name)

    click.confirm('Is the above information correct?', abort=True)
    print('Create Project (%s)' % name)


if __name__ == '__main__':
    cli()
