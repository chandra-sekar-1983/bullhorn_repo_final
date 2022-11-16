FROM google/cloud-sdk:366.0.0-alpine

RUN apk --update add openjdk8-jre && \
	gcloud components install cloud-datastore-emulator beta
