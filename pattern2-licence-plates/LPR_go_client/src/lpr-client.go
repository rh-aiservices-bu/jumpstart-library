package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net/http"
	"io/ioutil"
	"os"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
)

var (
	bucketName      string
  endpoint    string
	region    string

)

func init() {
  	flag.StringVar(&bucketName, "bucket", "public-license-plate-dataset", "S3 bucket name containing Image dataset")
		flag.StringVar(&region, "region", "ap-south-1", "S3 bucket region")
    flag.StringVar(&endpoint,  "endpoint", "http://license-plate-recognition-license-plate-recognition.apps.perf3.chris.ocs.ninja", "License Plate Recoginition service endpoint")
}

// Lists all objects in a bucket using pagination
func main() {
	flag.Parse()
	// Load the SDK's configuration from environment and shared config, and
	// create the client with this.
	cfg, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		log.Fatalf("failed to load SDK configuration, %v", err)
	}

	client := s3.NewFromConfig(cfg)

	// Set the parameters based on the CLI flag inputs.
	params := &s3.ListObjectsV2Input{
		Bucket: &bucketName,
	}

//	Create the Paginator for the ListObjectsV2 operation.
	p := s3.NewListObjectsV2Paginator(client, params, func(o *s3.ListObjectsV2PaginatorOptions) {
  })

	// Iterate through the S3 object pages, printing each object returned.
	var i int
	//log.Println("Objects:")
  fmt.Println("Detecting License Plate Number ...")
	rest_client := &http.Client{}
	apiUrl := "http://license-plate-recognition-license-plate-recognition.apps.perf3.chris.ocs.ninja/DetectPlateFromUrl/"

	req, err := http.NewRequest("POST",apiUrl, nil)
	if err != nil {
		log.Println(err)
		os.Exit(1)
	}

	q := req.URL.Query()

	for p.HasMorePages() {
		i++
		// Next Page takes a new context for each page retrieval. This is where
		// you could add timeouts or deadlines.
		page, err := p.NextPage(context.TODO())
		if err != nil {
			log.Fatalf("failed to get page %v, %v", i, err)
		}

		// Log the objects found
		for _, obj := range page.Contents {
			//fmt.Println("Object:", *obj.Key)
		
		q.Add("url", "https://" + bucketName +".s3." + region +".amazonaws.com/" + *obj.Key)
		req.URL.RawQuery = q.Encode()
	
		//fmt.Println(req.URL.String())
		req.Header.Set("Content-Type", "application/x-www-form-urlencoded; param=value") // This makes it work
	
		resp, err := rest_client.Do(req)
		if err != nil {
			log.Println(err)
		}
	
		f, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			log.Println(err)
		}
	
		resp.Body.Close()
		if err != nil {
			log.Fatal(err)
		}
		fmt.Println(string(f))
		//fmt.Println(resp.Status)

	}

}


}