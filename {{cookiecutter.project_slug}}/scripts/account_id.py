import json, os
slug = 'panorama_video_processor'
package_name = 'panorama_video_processor_logic'
with open(os.path.join(slug, 'graphs', slug, 'graph.json')) as f:
    graph = json.load(f)
for package in graph['nodeGraph']['packages']:
    if package['name'].endswith(package_name):
        print(package['name'].split('::')[0])
        break
