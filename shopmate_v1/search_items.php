<?php
$response = array();

if(isset($_POST["keyword_search"])){

    $keyword_search = $_POST["keyword_search"];
    $script_to_run = 'C:\xampp\htdocs\shopmate_v1\python\scrape_briefInfo.py';
    $result = shell_exec($script_to_run." "."\"".$keyword_search."\"");

    if(!empty($result)){
    
        //print_r($result); //this is only printing to human-readable form only no used.
        //echo $result; //this returns the original json object
       // $result_json_array = json_encode(json_decode($result,true)); //first decode it to associative array, and encode it back, will get array of json objects
                                                    //this ease the later parsing in java, first parse the array, then the object
                                                    // jsonArray for parsing [] but jsonObject parsing {}

        
                                                
        //this is the latest version: to standardize with the error response below so that the parsing will be easier and standard in java

        
        $result_json = json_decode($result);  
        $response["success"] = TRUE;
        $response["result"] = $result_json;
        echo json_encode(($response),true);


    }
    else{

        $response["success"] = FALSE;
        $response["message"] = "No products found";
        echo json_encode($response);

}

}
else{
    
    $response["success"] = FALSE;
    $response["message"] = "No products found";
    echo json_encode($response);

}

?>
