use std::io::Read;
use std::{path::Path, time::Duration};

#[cfg(windows)]
use std::path::PathBuf;

use criterion::{Criterion, criterion_group, criterion_main};

fn create_test_data() -> String {
    let temp_dir;
    let linux_dir;
    let kernel_path;
    #[cfg(unix)]
    {
        temp_dir = expanduser::expanduser("~/Rust/_Data/benches").unwrap();
        linux_dir = expanduser::expanduser("~/Rust/_Data/benches/linux-5.9").unwrap();
        kernel_path = expanduser::expanduser("~/Rust/_Data/benches/linux-5.9.tar.gz").unwrap();
    }
    #[cfg(windows)]
    {
        temp_dir = PathBuf::from("C:/Workspace/benches");
        linux_dir = PathBuf::from("C:/Workspace/benches/linux-5.9");
        kernel_path = PathBuf::from("C:/Workspace/benches/linux-5.9.tar.gz");
    }
    if !temp_dir.exists() {
        std::fs::create_dir_all(&temp_dir).unwrap();
    }
    if !kernel_path.exists() {
        // Download kernel
        println!("Downloading linux-5.9.tar.gz...");
        // ponytail: dev-only HTTPS kernel.org 下载，加固超时 + 大小上限（zip-bomb / 慢速攻击）
        const MAX_DOWNLOAD_BYTES: u64 = 2 * 1024 * 1024 * 1024; // 2 GB
        let client = reqwest::blocking::Client::builder()
            .timeout(Duration::from_secs(300))
            .build()
            .expect("client build failed");
        let resp = client
            .get("https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.9.tar.gz")
            .send()
            .expect("request failed");
        if !resp.status().is_success() {
            panic!("download failed: HTTP {}", resp.status());
        }
        if let Some(len) = resp.content_length()
            && len > MAX_DOWNLOAD_BYTES
        {
            panic!("download too large: {len} bytes (limit {MAX_DOWNLOAD_BYTES})");
        }
        let mut out = std::fs::File::create(&kernel_path).expect("failed to create file");
        // take() 流式 + 上限：替代 resp.text() 一次性载入，并阻断 Content-Length 与实际不符的放大
        let mut limited = resp.take(MAX_DOWNLOAD_BYTES + 1);
        let copied = std::io::copy(&mut limited, &mut out).expect("failed to copy content");
        if copied > MAX_DOWNLOAD_BYTES {
            panic!("download exceeded {MAX_DOWNLOAD_BYTES} bytes (got at least {copied})");
        }
    }
    if !linux_dir.exists() {
        println!("Extracting linux-5.9.tar.gz...");
        const MAX_EXTRACT_BYTES: u64 = 20 * 1024 * 1024 * 1024; // 20 GB
        let tar_gz = std::fs::File::open(&kernel_path).unwrap();
        let tar = flate2::read::GzDecoder::new(tar_gz);
        // ponytail: 限制解压总字节，阻断 tar-bomb
        let limited = tar.take(MAX_EXTRACT_BYTES);
        let mut archive = tar::Archive::new(limited);
        archive.unpack(&linux_dir).unwrap();
    }
    linux_dir.to_str().unwrap().to_string()
}

fn benchmark_dir(c: &mut Criterion, path: &str) {
    println!("Running benchmarks for {path}...");
    let dir = Path::new(path).file_name().unwrap().to_str().unwrap();
    let mut group = c.benchmark_group(format!("Count {dir}"));
    group.measurement_time(Duration::from_secs(10));
    group.sample_size(20);
    group.bench_function("scandir.Count (collect)", |b| {
        b.iter(|| {
            let mut instance = scandir::Count::new(path)
                .unwrap_or_else(|_| panic!("Failed to create Count instance for {path}"));
            instance.collect().unwrap();
        })
    });
    group.bench_function("scandir.Count(Ext) (collect)", |b| {
        b.iter(|| {
            let mut instance = scandir::Count::new(path)
                .unwrap_or_else(|_| panic!("Failed to create Count instance for {path}"))
                .extended(true);
            instance.collect().unwrap();
        })
    });
    group.finish();
}

fn benchmarks(c: &mut Criterion) {
    benchmark_dir(c, &create_test_data());
    #[cfg(unix)]
    let path = "/usr";
    #[cfg(windows)]
    let path = "C:/Windows";
    benchmark_dir(c, path);
}

criterion_group!(benches, benchmarks);
criterion_main!(benches);
