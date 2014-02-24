/**
 * Created by ljm4dk on 2/20/14.
 */

function password(val)
{

   // alert("Pin: " + val + ", " + val.length + ', ' + jQuery.isNumeric(val));
    if(val.length != 4 || !jQuery.isNumeric(val))
    {
        $('#password1').popover('show');

        return false;
    }
    else
    {
        $('#password1').popover('hide');
        return true;
    }
}

function passwordmatch(val1,val2)
{

    if(val1 === val2)
    {
        $('#password2').popover('hide');

        return true;
    }
    else
    {
        $('#password2').popover('show');
        return false;
    }
}