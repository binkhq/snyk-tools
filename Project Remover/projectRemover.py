import urllib3
import argparse
import json
import sys

# This is a script to manage the bulk deletion of projects from an Org in Snyk. Currently it only looks at the intergration
#used to import the project as a filter. This will be worked on to allow filtering via all fields within a project.



def get_projects(org, api_key):

    url = "https://snyk.io/api/v1/org/{orgid}/projects".format(orgid=org)

    response = http.request('POST', url, headers={
        'Content-Type': 'application/json',
        'Authorization': api_key
    })
    return json.loads(response.data.decode('UTF-8'))


def sort_projects(data, origin):
    sorted_projects = []
    for project in data['projects']:
        if project['origin'] == origin:
            sorted_projects.append(project)

    return sorted_projects

def project_lookup(project_id, org, api_key):

    url = "https://snyk.io/api/v1/org/{orgid}/project/{projectid}".format(orgid=org, projectid=project_id)

    response = http.request('GET', url, headers={
        'Content-Type': 'application/json',
        'Authorization': api_key
    })

    return json.loads(response.data.decode('UTF-8'))


def delete_projects(data, org, api_key):
    print("Projects selected for deletion: ")

    for project in data:
        print(project['name'])
    deletion_check = input("are you sure?: (y/n): ")

    if deletion_check[:1] != 'y':
        sys.exit()
    for project in data:
        try:
            message = "Deleting project {projectname}".format(projectname=project['name'])
            print(message)
            url = "https://snyk.io/api/v1/org/{orgid}/project/{projectid}".format(orgid=org, projectid=project['id'])

            response = http.request('DELETE', url, headers={
                'Content-Type': 'application/json',
                'Authorization': api_key
            })
        except Exception as e:
            print(e)

    print("Deletion Successful")


def delete_project(project, org, api_key):

    project_details = project_lookup(project, org, api_key)
    deletion_prompt = "The project {project} has been selected for deletion, are you sure? y/n".format(project=project_details['name'])
    deletion_check = input(deletion_prompt)
    if deletion_check[:1] != "y":
        sys.exit()
    try:
        message = "Deleting project {projectid}".format(projectid=project)
        print(message)
        url = "https://snyk.io/api/v1/org/{orgid}/project/{projectid}".format(orgid=org, projectid=project)

        response = http.request('DELETE', url, headers={
            'Content-Type': 'application/json',
            'Authorization': api_key
        })
        print("Project deleted")
    except Exception as e:
        print(e)
        print('project not deleted')

def main():
    parser = argparse.ArgumentParser(description='remove project(s) from Snyk')
    parser.add_argument('-o', '--org', dest='org', help='set org to remove from')
    parser.add_argument('-a', '--all', dest='all', help='remove all projects from select org')
    parser.add_argument('-O', '--origin', dest='origin', help='origin of the import e.g github')
    parser.add_argument('-A', '--api', dest='api', help='apikey')
    parser.add_argument('-p', '--project', dest='project', help='specify project to update')

    args = parser.parse_args()
    if args.api is None:
        print('Please supply a API key')
        sys.exit()
    else:
        api_key = args.api

    if args.org is None:
        print('please supply an org ID')
        sys.exit()

    if args.origin is None:

        if args.project is None:
            print('WARNING: This will delete all projects in the Org')
        else:
            delete_project(args.project, args.org, api_key)


    projects = get_projects(args.org, api_key)
    sorted_list = sort_projects(projects, args.origin)
    delete_projects(sorted_list, args.org, api_key)

    return

if __name__ =="__main__":
    http = urllib3.PoolManager()
    main()