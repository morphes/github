from django.shortcuts import render
from django.http import HttpResponse
from github import Github
from django.conf import settings
from datetime import date, datetime, timedelta
from django.template.defaulttags import register

g = Github(settings.GITHUB_TOKEN)

def index(request):            
    context = {
        'repositories': g.get_user().get_repos()
    }
    return render(request, 'statistic/index.html', context)
    
def commits(request, owner, name, month, day, year):    
    since = datetime(year, month, day)
    until = since + timedelta(days=1)
    
    repo_name = owner + '/' + name

    repository = g.get_repo(repo_name)    
    commits = repository.get_commits(since = since, until = until)
    
    context = {        
        'commits': commits,
        'date': since
    }
    return render(request, 'statistic/commits.html', context)

def repository(request, owner, name):        
    repo_name = owner + '/' + name
    repository = g.get_repo(repo_name)    

    since = datetime.today() - timedelta(days=settings.GITHUB_STATISTICS_DAYS)

    statistics = {}
    authors = []
    
    for collaborator in repository.get_collaborators():        
        authors.append(collaborator.login)

    for commit in repository.get_commits(since = since):
        
        commit_date = commit.commit.author.date.strftime('%m/%d/%Y')
        author_name = commit.author.login

        if commit_date in statistics:
            if author_name in statistics[commit_date]:
                statistics[commit_date][author_name] += 1
            else:
                statistics[commit_date][author_name] = 1
        else:
            statistics[commit_date] = {}
            statistics[commit_date][author_name] = 1

    dates = []

    result = {}
    for i in range(settings.GITHUB_STATISTICS_DAYS-1, -1, -1):                
        d = date.today() - timedelta(days=i)        
        commit_date = d.strftime('%m/%d/%Y')
        if(commit_date in statistics):
            for author in authors:
                if(author not in statistics[commit_date]):
                    statistics[commit_date][author] = 0                                
        else:
            statistics[commit_date] = {}
            for author in authors:
                statistics[commit_date][author] = 0
        result[commit_date] = statistics[commit_date]
        
    context = {
        'authors': authors,
        'statistics': result,
        'repository_id': repo_name
    }
    
    return render(request, 'statistic/repository.html', context)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
