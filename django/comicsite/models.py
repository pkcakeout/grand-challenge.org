import pdb
from userena.signals import signup_complete
from django.contrib.auth.models import Group,Permission

    
class ComicSiteException(Exception):
    """ any type of exception for which a django or python exception is not defined """
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
    

# =============================== permissions ===================================
# put permissions code here because signal receiver code should go into models.py
# according to https://docs.djangoproject.com/en/dev/topics/signals/#connecting-receiver-functions
# TODO: where should this code go? This does not seem like a good place for permissions

def set_project_admin_permissions(sender, **kwargs):
    user = kwargs['user']
    
    # add this user to the projectadminsgroup, which means user can see and edit standard
    # objects types in admin.
    projectadmingroup = get_or_create_projectadmingroup()
    user.groups.add(projectadmingroup)
    
    # set staff status so user can access admin interface. User will still have to 
    # activate through email link before being able to log in at all.
    user.is_staff = True
    user.save()
                
    

def get_or_create_projectadmingroup():
    """ create the group 'projectadmin' which should have class-level permissions for all 
    models a project admin can edit. E.g. add/change/delete comicsite, page, 
    dropboxfolder. If group does not exists, recreate with default permissions.
    """
    (projectadmins,created) = Group.objects.get_or_create(name='projectadmins')
    
    if created:
        add_standard_perms(projectadmins,"comicsite")
        add_standard_perms(projectadmins,"page")
        add_standard_perms(projectadmins,"dropboxfolder")
        
    return projectadmins
    

def add_standard_perms(group,classname):
    """ convenience function to add add_classname,change_classname,delete_classname
    permissions to permissionsgroup group
    """
    
    can_add = Permission.objects.get(codename="add_"+classname)
    can_change = Permission.objects.get(codename="change_"+classname)
    can_delete = Permission.objects.get(codename="delete_"+classname)
    
    group.permissions.add(can_add,can_change,can_delete)
    
    
    
# when a user activates account, set permissions. dispatch_uid makes sure the receiver is only
# registered once.  see https://docs.djangoproject.com/en/dev/topics/signals/ 
signup_complete.connect(set_project_admin_permissions,dispatch_uid="set_project_\
                            admin_permissions_reveiver") 

