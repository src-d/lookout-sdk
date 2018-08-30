package main

import (
	"context"
	"fmt"
	"io"
	"net"

	"google.golang.org/grpc"
	"gopkg.in/src-d/go-log.v1"
	"gopkg.in/src-d/lookout-sdk.v0/pb"
)

//implementes go.AnalyzerService
type analyzer struct{}

var portToListen = 2020
var dataSrvAddr = "localhost:10301"

func (*analyzer) NotifyReviewEvent(ctx context.Context, review *pb.ReviewEvent) (*pb.EventResponse, error) {
	log.Infof("got review request %v", review)

	conn, err := grpc.Dial(dataSrvAddr, grpc.WithInsecure())
	if err != nil {
		log.Errorf(err, "failed to connect to DataServer at %s", dataSrvAddr)
	}
	defer conn.Close()

	dataClient := pb.NewDataClient(conn)
	changes, err := dataClient.GetChanges(ctx, &pb.ChangesRequest{
		Head:            &review.Head,
		Base:            &review.Base,
		WantContents:    false,
		WantUAST:        true,
		ExcludeVendored: true,
	})
	if err != nil {
		log.Errorf(
			err, "GetChanges from DataServer %s failed", dataSrvAddr)
	}

	var comments []*pb.Comment
	for {
		change, err := changes.Recv()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Errorf(err, "GetChanges from DataServer %s failed", dataSrvAddr)
		}

		log.Infof("analyzing '%s' in %s", change.Head.Path, change.Head.Language)
		//TODO: put your analysis here!
		comments = append(comments, &pb.Comment{
			File: change.Head.Path,
			Line: 0,
			Text: fmt.Sprintf("language: %s", change.Head.Language),
		})
	}

	return &pb.EventResponse{Comments: comments}, nil
}

func (*analyzer) NotifyPushEvent(context.Context, *pb.PushEvent) (*pb.EventResponse, error) {
	return &pb.EventResponse{}, nil
}

func main() {
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", portToListen))
	if err != nil {
		log.Errorf(err, "failed to listen on port: %d", portToListen)
	}

	grpcServer := grpc.NewServer()
	pb.RegisterAnalyzerServer(grpcServer, &analyzer{})
	log.Infof("satart gRPC Analyzer server at port %d", portToListen)
	grpcServer.Serve(lis)
}
