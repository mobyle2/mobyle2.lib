import os


def which(name):
    """
    return the path of the executable corresponding to name
    mimic the which shell command
    
    :param name: the name of executable to find
    :type name: string
    :returns: the path of the executable or None if it not find
    :rtype: string
    """
    for path_dir in os.environ["PATH"].split(os.pathsep):
        path = os.path.join(path_dir, name)
        if os.access(path, os.X_OK):
            return path
