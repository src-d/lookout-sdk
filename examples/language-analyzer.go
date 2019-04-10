package main

import (
	"context"
	"fmt"
	"os"

	"google.golang.org/grpc"
	"gopkg.in/bblfsh/client-go.v2/tools"
	log "gopkg.in/src-d/go-log.v1"
	"gopkg.in/src-d/lookout-sdk.v0/go/sdk"
	"gopkg.in/src-d/lookout-sdk.v0/pb"
)

// Example Analyser gRPC service implementation.
// Posts file-level comments for every file
// with language detected and number of functions in the file.

type analyzer struct{}

var portToListen = 9930
var dataSrvAddr, _ = pb.ToGoGrpcAddress("ipv4://localhost:10301")
var version = "alpha"

func (*analyzer) NotifyReviewEvent(ctx context.Context, review *pb.ReviewEvent) (*pb.EventResponse, error) {
	logger := log.With(log.Fields(pb.GetLogFields(ctx)))

	logger.Infof("got review request %v", review)

	logFn := func(fields pb.Fields, format string, args ...interface{}) {
		// Do whatever you want with the provided fields
		msg := fmt.Sprintf(format, args...)
		logger.Infof("%s [%v]", msg, fields)
	}

	// Here you can also use pb.DialContext(ctx, dataSrvAddr)
	// if you don't want to log details of every connection
	conn, err := pb.DialContextWithInterceptors(
		ctx, dataSrvAddr,
		[]grpc.StreamClientInterceptor{
			pb.LogStreamClientInterceptor(logFn),
		},
		[]grpc.UnaryClientInterceptor{
			pb.LogUnaryClientInterceptor(logFn),
		},
	)
	if err != nil {
		logger.Errorf(err, "failed to connect to DataServer at %s", dataSrvAddr)
		return nil, err
	}
	defer conn.Close()

	dataClient := sdk.NewDataClient(conn)

	// Add some log fields that will be available to the data server
	// using `pb.AddLogFields`.
	ctx = pb.AddLogFields(ctx, pb.Fields{
		"some-string-key": "some-value",
		"some-int-key":    1,
	})

	changes, err := dataClient.GetChanges(ctx, &sdk.ChangesRequest{
		Head:            &review.Head,
		Base:            &review.Base,
		WantContents:    false,
		WantUAST:        true,
		ExcludeVendored: true,
	})
	if err != nil {
		logger.Errorf(err, "GetChanges from DataServer %s failed", dataSrvAddr)
		return nil, err
	}

	var comments []*pb.Comment
	for changes.Next() {
		change := changes.Change()
		if change.Head == nil {
			continue
		}

		logger.Infof("analyzing '%s' in %s", change.Head.Path, change.Head.Language)

		//TODO: put your analysis here!

		query := "//*[@roleFunction]"
		fns, err := tools.Filter(change.Head.UAST, query)
		if err != nil {
			logger.Errorf(err, "quering UAST from %s with %s failed", change.Head.Path, query)
			return nil, err
		}

		comments = append(comments, &pb.Comment{
			File: change.Head.Path,
			Line: 0,
			Text: fmt.Sprintf("language: %s, functions: %d", change.Head.Language, len(fns)),
		})
	}
	if err := changes.Err(); err != nil {
		logger.Errorf(err, "GetChanges from DataServer %s failed", dataSrvAddr)
		return nil, err
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

	logFn := func(fields pb.Fields, format string, args ...interface{}) {
		// Do whatever you want with the provided fields
		msg := fmt.Sprintf(format, args...)
		log.Infof("%s [%v]", msg, fields)
	}

	// Here you can also use pb.NewServer()
	// if you don't want to log details of every connection
	grpcServer := pb.NewServerWithInterceptors(
		[]grpc.StreamServerInterceptor{
			pb.LogStreamServerInterceptor(logFn),
		},
		[]grpc.UnaryServerInterceptor{
			pb.LogUnaryServerInterceptor(logFn),
		},
	)

	pb.RegisterAnalyzerServer(grpcServer, &analyzer{})
	log.Infof("starting gRPC Analyzer server at port %d", portToListen)
	grpcServer.Serve(lis)
}
