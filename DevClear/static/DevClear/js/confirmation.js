/**
 * Created by ljm4dk on 2/20/14.
 */

function confirm(key)
{
    if(key=="downgradeAdmin")
    {
        alert("Are you sure you want to remove this user as an administrator?");
        return false;
    }
    else if (key == "upgradeAdmin")
    {
        $('#myModal').modal("show")
        alert("Are you sure you want to add this member as an administrator?");
        return true;
    }
    else if (key == "removeMember")
    {
        alert("Are you sure you want to remove this user as a member?");
        return true;
    }

}