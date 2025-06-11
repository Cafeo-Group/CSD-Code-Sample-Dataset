from codeSamplesFetcher import CodeSamplesFetcher

fetcher = CodeSamplesFetcher()

def test_openCodeSamples():
    try:
        code_samples = fetcher.openCodeSamples()
        if code_samples:
            print("Code samples fetched successfully.")
            print("Total code samples:", len(code_samples))
            print(code_samples[1].strip())
            # for sample in code_samples:
            #     print(sample.strip())
        else:
            print("No code samples found.")
    except Exception as e:
        print("An error occurred:", str(e))

def test_parseCodeSamplesToJSON():
    try:
        parsed_samples = fetcher.parseCodeSamplesToJSON()
        if parsed_samples:
            print("Code samples parsed successfully.")
            print("Total parsed samples:", len(parsed_samples))
            print(parsed_samples[2])
            # for sample in parsed_samples:
            #     print(sample)
        else:
            print("No parsed samples found.")
    except Exception as e:
        print("An error occurred:", str(e))

def test_fetchCodeSamplesHtmls():
    try:
        html_urls = fetcher.fetchCodeSamplesHtmls()
        if html_urls:
            print("HTML URLs fetched successfully.")
            print("Total HTML URLs:", len(html_urls))
            print(html_urls[1])
            # for url in html_urls:
            #     print(url)
        else:
            print("No HTML URLs found.")
    except Exception as e:
        print("An error occurred:", str(e))

# TODO test fetchOwnsersAndReposFromUrls
    
# Run tests
# test_openCodeSamples()
test_fetchCodeSamplesHtmls()