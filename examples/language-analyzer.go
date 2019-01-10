package main

import (
	"context"
	"fmt"
	"io"
	"os"

	"gopkg.in/src-d/lookout-sdk.v0/pb"

	"google.golang.org/grpc"
	"gopkg.in/bblfsh/client-go.v2/tools"
	log "gopkg.in/src-d/go-log.v1"
)

// Example Analyser gRPC service implementation.
// Posts file-level comments for every file
// with language detected and number of functions in the file.

type analyzer struct{}

var portToListen = 9930
var dataSrvAddr, _ = pb.ToGoGrpcAddress("ipv4://localhost:10301")
var version = "alpha"

func (*analyzer) NotifyReviewEvent(ctx context.Context, review *pb.ReviewEvent) (*pb.EventResponse, error) {
	log.Infof("got review request %v", review)

	conn, err := pb.DialContext(ctx, dataSrvAddr, grpc.WithInsecure())
	if err != nil {
		log.Errorf(err, "failed to connect to DataServer at %s", dataSrvAddr)
		return nil, err
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
		log.Errorf(err, "GetChanges from DataServer %s failed", dataSrvAddr)
		return nil, err
	}

	var comments []*pb.Comment
	for {
		change, err := changes.Recv()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Errorf(err, "GetChanges from DataServer %s failed", dataSrvAddr)
			return nil, err
		}

		if change.Head == nil {
			continue
		}

		if change.Head == nil {
			continue
		}

		log.Infof("analyzing '%s' in %s", change.Head.Path, change.Head.Language)

		//TODO: put your analysis here!

		query := "//*[@roleFunction]"
		fns, err := tools.Filter(change.Head.UAST, query)
		if err != nil {
			log.Errorf(err, "quering UAST from %s with %s failed", change.Head.Path, query)
			return nil, err
		}

		comments = append(comments, &pb.Comment{
			File: change.Head.Path,
			Line: 0,
			Text: fmt.Sprintf("language: %s, functions: %d", change.Head.Language, len(fns)),
		})
	}

	return &pb.EventResponse{AnalyzerVersion: version, Comments: comments}, nil
}

func (*analyzer) NotifyPushEvent(context.Context, *pb.PushEvent) (*pb.EventResponse, error) {
	return &pb.EventResponse{}, nil
}

func main() {
	lis, err := pb.Listen(fmt.Sprintf("ipv4://0.0.0.0:%d", portToListen))
	if err != nil {
		log.Errorf(err, "failed to listen on port: %d", portToListen)
		os.Exit(1)
	}

	grpcServer := grpc.NewServer()
	pb.RegisterAnalyzerServer(grpcServer, &analyzer{})
	log.Infof("starting gRPC Analyzer server at port %d", portToListen)
	grpcServer.Serve(lis)
}
