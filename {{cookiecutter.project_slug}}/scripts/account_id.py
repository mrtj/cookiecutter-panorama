import json, os
slug = '{{cookiecutter.project_slug}}'
package_name = '{{cookiecutter.code_package_name}}'
with open(os.path.join(slug, 'graphs', slug, 'graph.json')) as f:
    graph = json.load(f)
for package in graph['nodeGraph']['packages']:
    if package['name'].endswith(package_name):
        print(package['name'].split('::')[0])
        break
