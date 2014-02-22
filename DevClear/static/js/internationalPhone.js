/**
 * Created by austi_000 on 2/1/14.
 */
function phonenumber(inputtxt)
{

    var international   = /^\+?([0-9]{2})\)?[-. ]?([0-9]{4})[-. ]?([0-9]{4})$/;
    var american        = /^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$/;

    if(inputtxt.match(international) || inputtxt.match(american))
    {
        return true;
    }
    else
    {
        alert("Not a valid Phone Number");
        return false;
    }
}