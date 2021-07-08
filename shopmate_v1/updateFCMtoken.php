<?php
require_once 'include/db_functions.php';
$db = new DB_Functions();


// json response array
$response = array("error" => FALSE);

if (isset($_POST['user_id']) && isset($_POST['token'])) {
 
    // receiving the post params
    $user_id = $_POST['user_id'];
    $token = $_POST['token'];

    $result = $db->updateFCMtoken($user_id,$token);
    if($result){
        $response["error"] = FALSE;
        $response["msg"] = "Token update successfully";
        echo json_encode($response);
    }
    else{
        $response["error"] = TRUE;
        $response["error_msg"] = "Token update failed";
        echo json_encode($response);
    }
    
    
} else {
    $response["error"] = TRUE;
    $response["error_msg"] = "Required parameters is missing!";
    echo json_encode($response);
}
?>