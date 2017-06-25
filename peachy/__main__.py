import click
import json
import os


def create_empty_file(file_path):
    with open(file_path, 'w'):
        pass


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
@click.option('--resources', prompt='Name of resource directory', type=str,
              default='res')
@click.option('--repo', prompt='Create a git repo', type=bool, default='n')
def createproject(name, author, email, url, main, resources, repo):
    """Create a new project."""
    # asset_directory name
    # Create git repo?
    '''scaffold
        .gitignore
        build.py
        config.json
        main.py
        game/
            res/
            __init__.py
            __main__.py
    '''
    package_name = name.lower().replace(' ', '_')
    package_name = click.prompt('Package Name', type=str, default=package_name)

    click.confirm('Is the above information correct?', abort=True)

    # Create project scaffold
    base_dir = os.getcwd()
    project_dir = os.path.join(base_dir, package_name)
    resource_dir = os.path.join(project_dir, resources)

    if os.path.exists(project_dir):
        click.confirm(
            'Project already exists. Would you like to replace it?',
            abort=True)
        if os.path.exists(resource_dir):
            os.rmdir(resource_dir)
        os.rmdir(project_dir)

    os.mkdir(project_dir)
    os.mkdir(resource_dir)

    # Create project config file
    config_data = {
        'project_name': name,
        'author': author,
        'author_email': email,
        'url': url,
        'main_entry': main,
        'resource_dir': resources
    }
    with open('config.json', 'w') as config_file:
        json.dump(config_data, config_file, indent=2)

    # Create project files
    create_empty_file(main)
    create_empty_file(os.path.join(project_dir, '__init__.py'))
    with open(os.path.join(resource_dir, 'outline.json'), 'w') as res_outline:
        json.dump({'resources': [], 'bundles': []}, res_outline, indent=2)

    print('Project created!')


if __name__ == '__main__':
    cli()
