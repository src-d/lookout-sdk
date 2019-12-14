package pb_test

import (
	"context"
	"fmt"
	"net"
	"testing"
	time "time"

	"gopkg.in/meyskens/lookout-sdk.v0/pb"

	"github.com/stretchr/testify/suite"
	grpc "google.golang.org/grpc"
)

// Implements AnalyzerClient interface
type mockAnalyzer struct {
	Callback func(ctx context.Context)
}

func (a *mockAnalyzer) NotifyReviewEvent(ctx context.Context, event *pb.ReviewEvent) (*pb.EventResponse, error) {
	if a.Callback != nil {
		a.Callback(ctx)
	}
	return &pb.EventResponse{}, nil
}

func (a *mockAnalyzer) NotifyPushEvent(ctx context.Context, event *pb.PushEvent) (*pb.EventResponse, error) {
	if a.Callback != nil {
		a.Callback(ctx)
	}
	return &pb.EventResponse{}, nil
}

const port = 50050

// GrpcSuite is this file's main test suite
type GrpcSuite struct {
	suite.Suite

	listener   net.Listener
	grpcServer *grpc.Server
	grpcAddr   string
}

func TestGrpcSuite(t *testing.T) {
	suite.Run(t, new(GrpcSuite))
}

func (s *GrpcSuite) SetupSuite() {
	var err error
	s.grpcAddr, err = pb.ToGoGrpcAddress(fmt.Sprintf("ipv4://127.0.0.1:%d", port))
	s.Require().NoError(err)
}

func (s *GrpcSuite) TearDownTest() {
	s.grpcServer.Stop()
	s.listener.Close()
}

func (s *GrpcSuite) startServer() {
	var err error
	s.listener, err = pb.Listen(fmt.Sprintf("ipv4://0.0.0.0:%d", port))
	s.Require().NoError(err, "failed to listen on port: %d", port)

	err = s.grpcServer.Serve(s.listener)
	s.Require().NoError(err)
}

func (s *GrpcSuite) TestAnalyzerService() {
	// Basic test for the Analyzer service methods

	require := s.Require()

	s.grpcServer = pb.NewServer()
	pb.RegisterAnalyzerServer(s.grpcServer, &mockAnalyzer{})

	go s.startServer()
	// Wait for the server to start listening
	time.Sleep(time.Second)

	conn, err := pb.DialContext(context.TODO(), s.grpcAddr)
	require.NoError(err)

	client := pb.NewAnalyzerClient(conn)

	res, err := client.NotifyReviewEvent(context.TODO(), &pb.ReviewEvent{})
	require.NoError(err)
	require.NotNil(res)

	res, err = client.NotifyPushEvent(context.TODO(), &pb.PushEvent{})
	require.NoError(err)
	require.NotNil(res)
}

func (s *GrpcSuite) TestAnalyzerCtxlogInterceptor() {
	// In this scenario we use pb.AddFields before the gRPC call is started,
	// and pb.GetLogFields inside the gRPC handler.

	require := s.Require()

	var serverFields pb.Fields

	s.grpcServer = pb.NewServer()
	pb.RegisterAnalyzerServer(s.grpcServer, &mockAnalyzer{
		Callback: func(ctx context.Context) {
			serverFields = pb.GetLogFields(ctx)
		},
	})

	go s.startServer()
	// Wait for the server to start listening
	time.Sleep(time.Second)

	conn, err := pb.DialContext(context.TODO(), s.grpcAddr)
	require.NoError(err)

	client := pb.NewAnalyzerClient(conn)

	clientFields := pb.Fields{
		"key-A": "value-A",
	}
	ctx := pb.AddLogFields(context.TODO(), clientFields)

	res, err := client.NotifyReviewEvent(ctx, &pb.ReviewEvent{})
	require.NoError(err)
	require.NotNil(res)
	require.EqualValues(clientFields, serverFields)

	// New context, replaces the fields
	clientFields = pb.Fields{
		"key-B": "value-B",
	}
	ctx = pb.AddLogFields(context.TODO(), clientFields)

	res, err = client.NotifyPushEvent(ctx, &pb.PushEvent{})
	require.NoError(err)
	require.NotNil(res)
	require.EqualValues(clientFields, serverFields)
}

func (s *GrpcSuite) TestAnalyzerAddLogFieldsInterceptor() {
	// In this scenario we use pb.AddFields in a client interceptor,
	// and pb.GetLogFields in a server interceptor

	require := s.Require()

	var serverFields pb.Fields

	myUnaryServerInterceptor := func(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
		serverFields = pb.GetLogFields(ctx)
		return handler(ctx, req)
	}

	myStreamServerInterceptor := func(srv interface{}, stream grpc.ServerStream, info *grpc.StreamServerInfo, handler grpc.StreamHandler) error {
		ctx := stream.Context()
		serverFields = pb.GetLogFields(ctx)
		return handler(srv, stream)
	}

	s.grpcServer = pb.NewServerWithInterceptors(
		[]grpc.StreamServerInterceptor{myStreamServerInterceptor},
		[]grpc.UnaryServerInterceptor{myUnaryServerInterceptor},
	)
	pb.RegisterAnalyzerServer(s.grpcServer, &mockAnalyzer{})

	go s.startServer()
	// Wait for the server to start listening
	time.Sleep(time.Second)

	var clientFields pb.Fields

	myUnaryClientInterceptor := func(ctx context.Context, method string, req, reply interface{}, cc *grpc.ClientConn, invoker grpc.UnaryInvoker, opts ...grpc.CallOption) error {
		ctx = pb.AddLogFields(context.TODO(), clientFields)
		return invoker(ctx, method, req, reply, cc, opts...)
	}

	myStreamClientInterceptor := func(ctx context.Context, desc *grpc.StreamDesc, cc *grpc.ClientConn, method string, streamer grpc.Streamer, opts ...grpc.CallOption) (grpc.ClientStream, error) {
		ctx = pb.AddLogFields(context.TODO(), clientFields)
		return streamer(ctx, desc, cc, method, opts...)
	}

	conn, err := pb.DialContextWithInterceptors(context.TODO(), s.grpcAddr,
		[]grpc.StreamClientInterceptor{myStreamClientInterceptor},
		[]grpc.UnaryClientInterceptor{myUnaryClientInterceptor},
	)
	require.NoError(err)

	client := pb.NewAnalyzerClient(conn)

	clientFields = pb.Fields{
		"key-A": "value-A",
	}

	res, err := client.NotifyReviewEvent(context.TODO(), &pb.ReviewEvent{})
	require.NoError(err)
	require.NotNil(res)
	require.EqualValues(clientFields, serverFields)

	// New context, replaces the fields
	clientFields = pb.Fields{
		"key-B": "value-B",
	}

	res, err = client.NotifyPushEvent(context.TODO(), &pb.PushEvent{})
	require.NoError(err)
	require.NotNil(res)
	require.EqualValues(clientFields, serverFields)
}
