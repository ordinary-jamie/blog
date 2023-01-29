GCP_PROFILE=default
GCP_PROJECT=blog-jamphan-dev
GCP_BUCKET=www.jamphan.dev


clean:
	rm -rf ./dist

build: clean
	python gen.py
	npm run build

serve:
	python gen.py --data data --output src/assets --post-ext md
	@npm run dev

publish: clean build
	gcloud config configurations activate $(GCP_PROFILE)
	gcloud config set project $(GCP_PROJECT)
	gsutil -m rsync -R ./dist gs://$(GCP_BUCKET)