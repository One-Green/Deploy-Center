from git.exc import GitCommandError


def refresh_branch(repo, remote_url, branch):
    repo.git.fetch('--all')
    try:
        # repo.git.execute(["git", "checkout", "--track", f"origin/{branch}"])
        repo.git.checkout("-b", branch)
    except GitCommandError:
        repo.git.checkout(branch)

    repo.git.reset('--hard')
    repo.git.clean('-fdx')
    if 'upstream' not in repo.remotes:
        repo.create_remote('upstream', url=remote_url)
        repo.remotes.upstream.fetch()
    repo.git.pull('origin', branch)
    repo.git.pull('upstream', branch)
